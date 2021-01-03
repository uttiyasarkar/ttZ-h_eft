########################OA
### Skim data        ###
### for analysis     ###
########################
### written by:      ###
### Bryan Caraway    ###
########################
##
#
import uproot
import os
import re
import sys
if __name__ == '__main__':
    import subprocess as sb
    sys.path.insert(1, sb.check_output('echo $(git rev-parse --show-cdup)', shell=True).decode().strip('\n')+'DeepSleep/')
import time
from collections import defaultdict
from numba import njit, prange
import concurrent.futures
import functools
#
import config.ana_cff as cfg
from lib.fun_library import fillne, t2Run
from modules.AnaDict import AnaDict
from modules.AnaVars import AnaVars
#
import numpy as np
np.random.seed(0)
import pandas as pd
##


class Skim :
    '''
    This code does two things:
    1. define analysis objects: leptons, jets, fatjets, bjets
    2. apply event level cuts/filters to elliminate unwanted events
    3. (for data) apply golden json file
    '''
    @t2Run
    def __init__(self, roofile, sample, year, isData=False, jec_sys=None, jec_type=None):
        self.roofile = roofile
        self.sample = sample
        self.year   = year
        self.isData = isData
        #
        self.jec_sys  = jec_sys if jec_sys else ''
        self.ana_vars = AnaVars(year,isData, jec_sys=jec_sys, jec_type=jec_type) 
        self.tree     = self.set_tree_from_roofile(roofile)
        # define event information
        self.jets      = self.build_dict(cfg.ana_vars['ak4vars']+cfg.ana_vars['ak4lvec']['TLVars']) 
        self.fatjets   = self.build_dict(cfg.ana_vars['ak8vars']+cfg.ana_vars['ak8lvec']['TLVars'])
        self.electrons = self.build_dict(cfg.lep_sel_vars['electron']) 
        self.muons     = self.build_dict(cfg.lep_sel_vars['muon']) 
        self.events    = self.build_dict(cfg.ana_vars['event']+(
            (cfg.ana_vars['sysvars_mc']+cfg.ana_vars[f'sysvars_{self.year}']) 
            if not self.isData else []))  
        # other things like gen info
        self.geninfo    = self.build_dict(cfg.ana_vars['genpvars']) 
        self.hlt        = self.build_dict(cfg.ana_vars['dataHLT_all']+cfg.ana_vars[f'dataHLT_{self.year}'])
        self.subjets    = self.build_dict(cfg.ana_vars['ak8sj'])
        # wont keep
        self.lheweights = self.build_dict(cfg.ana_vars['lheWeights'])
        self.filters    = self.build_dict(cfg.ana_vars['filters']) 
        # ===================== #
        # define object criteria
        self.jet_mask     = self.is_a_jet()
        self.fatjet_mask  = self.is_a_fatjet()
        self.elec_mask    = self.is_a_electron()
        self.muon_mask    = self.is_a_muon()
        # apply object criteria
        self.jets      = self.jets[     self.jet_mask]
        self.fatjets   = self.fatjets[  self.fatjet_mask]
        self.electrons = self.electrons[self.elec_mask]
        self.muons     = self.muons[    self.muon_mask]
        # define event selection
        self.event_mask   = self.get_event_selection()
        # apply event selection
        self.jets       = self.jets[      self.event_mask]
        self.fatjets    = self.fatjets[   self.event_mask]
        self.electrons  = self.electrons[ self.event_mask]
        self.muons      = self.muons[     self.event_mask]
        self.events     = self.events[    self.event_mask]
        self.geninfo    = self.geninfo[   self.event_mask]
        self.lheweights = self.lheweights[self.event_mask]
        self.subjets    = self.subjets[   self.event_mask]
        ''' 
        add interesting info to events: 
        (lepton pt, eta, phi , etc...) 
        njets, nfjets, nbjets
        ps, sc, eft
        hem veto weight
        '''
        self.handle_lheweights()
        self.handle_lep_info()
        self.handle_multiplicity_info()
        #
    #
    def get_skim(self):
        __out_wrapper = {
            'ak4':self.jets,
            'ak8':self.fatjets.update(self.subjets),
            'gen':self.geninfo,
            'events':self.events,
        }
        return __out_wrapper
            

    # === functions to add info to events === #
    def handle_lheweights(self):
        ps_w  = self.lheweights['PSWeight'].pad(4).fillna(1)
        sc_w  = self.lheweights['LHEScaleWeight'].pad(9).fillna(1)
        self.events['ISR_Up']   = ps_w[:,2]
        self.events['ISR_Down'] = ps_w[:,0]
        self.events['FSR_Up']   = ps_w[:,3]
        self.events['FSR_Down'] = ps_w[:,1]
        #
        self.events['mu_r_Up']    = sc_w[:,7]
        self.events['mu_r_Down']  = sc_w[:,1]
        self.events['mu_f_Up']    = sc_w[:,5]
        self.events['mu_f_Down']  = sc_w[:,3]
        self.events['mu_rf_Up']   = sc_w[:,8]
        self.events['mu_rf_Down'] = sc_w[:,0]
        #
        if 'EFT' in self.sample:
            eft_w =  self.lheweights['LHEReweightingWeight'].pad(184).fillna(1)
            for i in range(184):
                self.events[f'EFT{i}'] = eft_w[:,i]

        
    #
    def handle_lep_info(self): # assumes event filter already applied (1 lepton per event)
        from awkward import JaggedArray as aj
        get_lep_info = (lambda k : aj.concatenate(
            [self.muons[f'Muon_{k}'], self.electrons[f'Electron_{k}']], axis=1).flatten()
        )
        single_mu = (self.muons['Muon_pt'].counts         == 1)
        single_el = (self.electrons['Electron_pt'].counts == 1)
        self.events.update({
            'Lep_pt'  : get_lep_info('pt'),
            'Lep_eta' : get_lep_info('eta'),
            'Lep_phi' : get_lep_info('phi'),
            'Lep_mass': get_lep_info('mass'),
            'passSingleLepMu'   : single_mu,
            'passSingleLepElec' : single_el
        })
    #
    def handle_multiplicity_info(self):
        self.events.update({
            'n_ak4jets': self.jets['Jet_pt'].counts,
            'n_ak8jets': self.fatjets['FatJet_pt'].counts,
            'nBottoms' : self.jets['Jet_pt'][(self.jets['Jet_btagDeepB'] > cfg.ZHbb_btagWP[self.year])].counts
        })
    # === object criteria functions === #
    def is_a_jet(self):
        return  ((self.jets['Jet_pt']       > 30) & 
                 (abs(self.jets['Jet_eta']) < 2.4) & 
                 ((self.jets['Jet_pt'] > 50) | (self.jets['Jet_puId'] >= 4) ) &
                 ( self.jets['Jet_jetId'] >= 2))
    #
    def is_a_fatjet(self):
        return ((self.fatjets['FatJet_pt'] >  200) &
                (abs(self.fatjets['FatJet_eta']) < 2.4) &   
                (self.fatjets['FatJet_msoftdrop'] >= 50) & 
                (self.fatjets['FatJet_msoftdrop'] <= 200) & 
                ( self.fatjets['FatJet_jetId'] >= 2))
                        
    #
    def is_a_electron(self):
        return  cfg.lep_sel['electron'][self.year](self.electrons)
    #
    def is_a_muon(self):
        return cfg.lep_sel['muon'](self.muons)
    # === event criteria functions === #
    def get_MET_filter(self) :    
        return ((self.filters['Flag_goodVertices']                       == 1)       &
                (self.filters['Flag_globalSuperTightHalo2016Filter']     == 1)       &
                (self.filters['Flag_HBHENoiseFilter']                    == 1)       & 
                (self.filters['Flag_HBHENoiseIsoFilter']                 == 1)       & 
                (self.filters['Flag_EcalDeadCellTriggerPrimitiveFilter'] == 1)       & 
                (self.filters['Flag_BadPFMuonFilter']                    == 1)       &
                ((self.filters['Flag_eeBadScFilter'] == 1) if self.isData else True) &
                ((self.filters['Flag_ecalBadCalibFilterV2'] == 1) 
                 if (self.year == '2017' or self.year == '2018') else True )
        )
    #
    def get_HEM_veto(self) : 
        elec_hem = lambda : ((self.electrons['Electron_pt'] > 20 )    &
                             (self.electrons['Electron_eta'] < -3.0)  &
                             (self.electrons['Electron_eta'] > -1.4)  &
                             (self.electrons['Electron_phi'] < -0.87) &
                             (self.electrons['Electron_phi'] > -1.57))
        jet_hem  = lambda : ((self.jets['Jet_pt']  > 30 )    &
                             (self.jets['Jet_eta'] < -3.0)  &
                             (self.jets['Jet_eta'] > -1.3)  &
                             (self.jets['Jet_phi'] < -0.87) &
                             (self.jets['Jet_phi'] > -1.57))
        #return True # think about how to do this (add hem weight helper function)
        return ~( ( self.electrons['Electron_pt'][elec_hem()].counts > 0 ) | 
                  ( self.jets['Jet_pt'][jet_hem()].counts > 0 ) )
        
    #
    def get_event_selection(self): # after objects have been defined
        return ( (self.jets['Jet_pt'].counts >= 4) &
                 (self.fatjets['FatJet_pt'].counts >= 1) &
                 (self.jets['Jet_pt'][(self.jets['Jet_btagDeepB'] > cfg.ZHbb_btagWP[self.year])].counts >= 2) &
                 (self.events['MET_pt'] > 20) &
                 (self.electrons['Electron_pt'].counts + self.muons['Muon_pt'].counts == 1) &
                 self.get_MET_filter() #&
                 #(self.get_HEM_veto() if (self.year == '2018' and self.isData) else True)
             )
    # === helper functions === #
    def set_tree_from_roofile(self,roofile, estart=None, estop=None):
        ''' Set tree array method and tree pandas method '''
        f = uproot.open(self.roofile)
        #print(estart, estop)
        tree         =  f.get('Events') # hardcoded
        self.tarray  = functools.partial(tree.array,      entrystart=estart, entrystop=estop)
        self.tpandas = functools.partial(tree.pandas.df , entrystart=estart, entrystop=estop)
        return tree

    def build_dict(self, keys, with_interp=True):
        executor = concurrent.futures.ThreadPoolExecutor()
        if with_interp:
            return AnaDict({k: self.tarray(self.ana_vars[k], executor=executor) for k in keys})
        else:
            return AnaDict({k: self.tarray(k, executor=executor) for k in keys})
    # === ~ Skim class === #
                
if __name__ == '__main__':
    #test_file = '/cms/data/store/user/bcaraway/NanoAODv7/PostProcessed/2018/ttHTobb_2018/839BA380-7826-9140-8C16-C5C0903EE949_Skim_12.root'
    #test_file  = '/cms/data/store/user/bcaraway/NanoAODv7/PostProcessed/2018/TTToSemiLeptonic_2018/D6501B6C-8B76-BF42-B677-64680733A780_Skim_19.root'
    test_file   = '/cms/data/store/user/bcaraway/NanoAODv7/PostProcessed/2017/TTToSemiLeptonic_2017/DEDD55D3-8B36-3342-8531-0F2F4C462084_Skim_134.root' 
    _ = Skim(test_file, 'ttHTobb', '2018', isData=False, jec_sys=None, jec_type=None)
    AnaDict(_.get_skim()).to_pickle('testoutput.pkl')
    
