################
## Config for ##
# TTV analysis #
################
#
import subprocess as sb
# get current working directory according to git
def cdir():
    _cdir = sb.check_output('pwd', shell=True).decode().strip('\n')
    if 'condor' in _cdir: _wdir = './' # if working on condor, already in the right directory
    else:
        _wdir = sb.check_output('echo $(git rev-parse --show-toplevel)', shell=True).decode().strip('\n')+'/DeepSleep/'
    return _wdir, _cdir

_wdir, _cdir = cdir()
#
master_file_path  = _wdir+'files/'
dataDir           = _wdir+'data/'
pdfDir            = _wdir+'pdf/'
#### NanoAODv7 PostProcessed Sample Directory ####
preproc_dir = '/cms/data/store/user/bcaraway/NanoAODv7/PreProcessed/'
postproc_dir = '/cms/data/store/user/bcaraway/NanoAODv7/PostProcessed/'
postSkim_dir = '/cms/data/store/user/ttxeft/NanoAODv7/Skim/'
# Overhead #
import os
if   os.path.exists('/cms/data/store/user/ttxeft/') : # test to see if on kodiak
    file_path         = '/cms/data/store/user/ttxeft/Skim_nanoAOD/' # for kodiak
elif os.path.exists('/eos/uscms/') or 'condor' in _cdir: # test to see if on lpc will need to fix for condor on kodiak i think
    file_path        = 'root://cmseos.fnal.gov//store/user/bcaraway/skimAnaSamples/'
    preproc_dir  = preproc_dir.replace('/cms/data','/eos/uscms').replace('ttxeft','bcaraway')
    postproc_dir = postproc_dir.replace('/cms/data','/eos/uscms').replace('ttxeft','bcaraway')
    postSkim_dir = postSkim_dir.replace('/cms/data','/eos/uscms').replace('ttxeft','bcaraway')
else: raise("Not on Kodiak or LPC, please manually input file_path in file: ./config/ana_cff.py")

##
ZHptcut           = 200
Years             = ['2016','2017','2018']
## EFT ##
Sig_EFT_MC        = ['TTZ_EFT','TTH_EFT']
tt_eft_samples    = ['TTJets_EFT','TTBB_EFT']
#########
Sig_MC            = ['ttH','ttZ']
Bkg_MC            = ['TTBar','ttbb','ttX','single_t','VV','VVV','VJets']
All_MC            = ['ttZ','ttH','TTBar','ttbb','single_t','ttX','VV','VVV','VJets']

# Handle systematic sample docs
tt_sys_samples    = ['TTBar_UEUp','TTBar_UEDown','TTBar_hdampUp','TTBar_hdampDown',
                     'ttbb_hdampUp','ttbb_hdampDown']
tt_bb             = ['ttbb',]
tt_bb_sys         = [ 'ttbb_hdampUp','ttbb_hdampDown', ]

#
#jec_variations    = [jtype+jec for jec in ['JESUp','JESDown','JERUp','JERDown'] for jtype in ['ak4','ak8']]
jecs              = [jec+y for jec in ['jesRelativeSample','jesHF' , 'jesAbsolute', 'jesEC2', 'jesBBEC1'] for y in Years] + \
                    ['jesHF' , 'jesAbsolute', 'jesEC2', 'jesBBEC1', 'jesRelativeBal', 'jesFlavorQCD',
                     'jesHEMIssue',  # 2018 only 
                     'ak4jer','ak8jer', # jer
                     'jms','jmr'] # puppi sdm corr
jec_variations    = [jec+ud for jec in jecs for ud in ['Up','Down']]
sig_sys_samples   = [sig+'_'+jec for sig in Sig_MC for jec in jec_variations]
bkg_sys_samples   = [bkg+'_'+jec for bkg in Bkg_MC for jec in jec_variations] + tt_sys_samples
all_sys_samples   = sig_sys_samples + bkg_sys_samples
#
Data_samples      = ['Single_Electron','Single_Muon']
Lumi              = {'2016': 35.917149,
                     '2017': 41.525338,
                     '2018': 59.72444,
                     '2018preHEM' : 21.1,
                     '2018postHEM': 38.6,
                     'run2': 137.166648,
                     'Total': 137.166648
                  } 
goodLumis_file   = {
    #'2016':dataDir+'/good_lumis/'+'Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt',  # may change to re-reco
    '2016':dataDir+'/good_lumis/'+'Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt', # re-reco
    #'2017':dataDir+'/good_lumis/'+'Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt',# may change to re-reco
    '2017':dataDir+'/good_lumis/'+'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt', # re-reco
    #'2018':dataDir+'/good_lumis/'+'Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt',  # may change to re-reco
    '2018':dataDir+'/good_lumis/'+'Cert_314472-325175_13TeV_17SeptEarlyReReco2018ABC_PromptEraD_Collisions18_JSON.txt', # re-reco
}
##
##############
##### TTZ, Z to bb CONFIG #####
ZHbbFitMinJets = 4
ZHbbFitMaxJets = 100
ZHbb_btagWP    = {'2016': 0.6321, # Med for 2016
                  '2017': 0.4941, # Med for 2017
                  '2018': 0.4148  # Med for 2018
                  }
# ttZ/H->bb SM x-section
ZHbbXsec = {'ttZbb': .1157,
            'ttHbb': .2934 }
ZHbbtotXsec = ZHbbXsec['ttZbb'] + ZHbbXsec['ttHbb']
# ttZ/H->bb MC count 2017
n_ZHbbMC_dict      = {'ttZbb': 163876,
                      'ttHbb': 5698653 }
n_ZHbbMC           = n_ZHbbMC_dict['ttZbb'] + n_ZHbbMC_dict['ttHbb']
#
hlt_path = {
    'muon'    :{ '2016': (lambda x : ((x['HLT_IsoMu24']) | 
                                      (x['HLT_IsoTkMu24']) | 
                                      (x['HLT_Mu50']) | 
                                      (x['HLT_TkMu50']))),

                 '2017': (lambda x : ((x['HLT_IsoMu27']) | 
                                      (x['HLT_Mu50']) | 
                                      (x['HLT_OldMu100']) | 
                                      (x['HLT_TkMu100']))),

                 '2018': (lambda x : ((x['HLT_IsoMu24']) | 
                                      (x['HLT_Mu50']) | 
                                      (x['HLT_OldMu100']) | 
                                      (x['HLT_TkMu100']))),
             },
    'electron':{ '2016': (lambda x : ((x['HLT_Ele27_WPTight_Gsf']) | 
                                      (x['HLT_Photon175']) | 
                                      (x['HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165']) | 
                                      (x['HLT_Ele115_CaloIdVT_GsfTrkIdT']) | 
                                      (x['HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50']))),

                 '2017': (lambda x : ((x['HLT_Ele32_WPTight_Gsf_L1DoubleEG']) | 
                                      (x['HLT_Ele35_WPTight_Gsf']) | 
                                      (x['HLT_Photon200']) | 
                                      (x['HLT_Ele115_CaloIdVT_GsfTrkIdT']) | 
                                      (x['HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165']) #|
                                      #(x['HLT_Ele28_eta2p1_WPTight_Gsf_HT150']) # trying this out
                                  )),

                 '2018': (lambda x : ((x['HLT_Ele32_WPTight_Gsf']) | 
                                      (x['HLT_Ele115_CaloIdVT_GsfTrkIdT']) | 
                                      (x['HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165']) | 
                                      (x['HLT_Photon200']) #|
                                      #(x['HLT_Ele28_eta2p1_WPTight_Gsf_HT150']) # trying this out
                                  ))
             }
}
###################
# Input Variables #
#LC = '_drLeptonCleaned'
LC = ''
#
lep_sel_vars = {'muon'    : ['Muon_pt','Muon_eta','Muon_phi','Muon_mass',
                             'Muon_miniPFRelIso_all','Muon_mediumId'],#'Muon_FlagId'],
                'electron': ['Electron_pt','Electron_eta','Electron_phi','Electron_mass',
                             'Electron_miniPFRelIso_all', 'Electron_cutBasedNoIso']}

lep_sel =      {'muon': (lambda x: ((x['Muon_pt'] > 30)        & 
                                    (abs(x['Muon_eta']) < 2.4) &
                                    #(x['Muon_FlagId'] >= 1)    &  # not in NanoAODv7 files
                                    (x['Muon_mediumId'] >= 1)    & 
                                    (x['Muon_miniPFRelIso_all'] < 0.2) )),

                'electron': {'2016': (lambda x : ((x['Electron_pt'] > 30) & (abs(x['Electron_eta']) < 2.5) & 
                                                  (x['Electron_cutBasedNoIso'] >= 4) & (x['Electron_miniPFRelIso_all'] < 0.1))),
                             '2017': (lambda x : ((x['Electron_pt'] > 35) & (abs(x['Electron_eta']) < 2.5) & 
                                                  (x['Electron_cutBasedNoIso'] >= 4) & (x['Electron_miniPFRelIso_all'] < 0.1))),
                             '2018': (lambda x : ((x['Electron_pt'] > 35) & (abs(x['Electron_eta']) < 2.5) & 
                                                  (x['Electron_cutBasedNoIso'] >= 4) & (x['Electron_miniPFRelIso_all'] < 0.1))),
                             }
                }

ana_vars = {
    'ak4vars'    : ['Jet_btagDeepB','Jet_puId','Jet_jetId',],
    'ak4mcvars'  : ['Jet_btagSF_deepcsv_shape',
                    'Jet_btagSF_deepcsv_shape_up_jes','Jet_btagSF_deepcsv_shape_down_jes',
                    'Jet_btagSF_deepcsv_shape_up_hf','Jet_btagSF_deepcsv_shape_down_hf',
                    'Jet_btagSF_deepcsv_shape_up_lf','Jet_btagSF_deepcsv_shape_down_lf',
                    'Jet_btagSF_deepcsv_shape_up_hfstats1','Jet_btagSF_deepcsv_shape_down_hfstats1',
                    'Jet_btagSF_deepcsv_shape_up_lfstats1','Jet_btagSF_deepcsv_shape_down_lfstats1',
                    'Jet_btagSF_deepcsv_shape_up_hfstats2','Jet_btagSF_deepcsv_shape_down_hfstats2',
                    'Jet_btagSF_deepcsv_shape_up_lfstats2','Jet_btagSF_deepcsv_shape_down_lfstats2',],
    # 'Jet_deepFlavourlepb'+LC, 'Jet_deepFlavouruds'+LC, 'Jet_deepFlavourb'+LC, 'Jet_deepFlavourbb'+LC],
    'ak4lvec'    : {'TLV'         :['JetTLV'+LC],
                    'TLVarsLC'    :['Jet_pt'+LC, 'Jet_eta'+LC, 'Jet_phi'+LC, 'Jet_mass'+LC],
                    'TLVars'      :['Jet_pt', 'Jet_eta', 'Jet_phi', 'Jet_mass'],
                    'jesTotUp'    :['Jet_pt_jesTotalUp', 'Jet_eta' 'Jet_phi', 'Jet_mass_jesTotalUp'],
                    'jesTotDown'  :['Jet_pt_jesTotalDown', 'Jet_eta' 'Jet_phi', 'Jet_mass_jesTotalDown'],
                    'jerUp'       :['Jet_pt_jerUp', 'Jet_eta' 'Jet_phi', 'Jet_mass_jerUp'],
                    'jerDown'     :['Jet_pt_jerDown', 'Jet_eta' 'Jet_phi', 'Jet_mass_jerDown'],
                },
#
    'ak8vars'    : ['FatJet_jetId',
                    'FatJet_deepTagMD_WvsQCD','FatJet_deepTagMD_TvsQCD','FatJet_deepTagMD_bbvsLight',
                    'FatJet_deepTagMD_ZHbbvsQCD',
                    #'FatJet_deepTag_WvsQCD'+LC,'FatJet_deepTag_TvsQCD'+LC,'FatJet_deepTag_ZvsQCD'+LC,
                    #'FatJet_deepTagMD_H4qvsQCD'+LC, 'FatJet_deepTagMD_HbbvsQCD'+LC, 'FatJet_deepTagMD_TvsQCD'+LC, 
                    #'FatJet_deepTagMD_ZbbvsQCD'+LC, 'FatJet_deepTagMD_ZvsQCD'+LC, 'FatJet_deepTagMD_bbvsLight'+LC, 'FatJet_deepTagMD_ccvsLight'+LC,     
                    'FatJet_msoftdrop'+LC,'FatJet_btagDeepB'+LC,'FatJet_btagHbb'+LC,
                    'FatJet_subJetIdx1'+LC,'FatJet_subJetIdx2'+LC],
    'ak8lvec'    : {'TLV'      :['FatJetTLV'+LC],
                    'TLVarsLC' :['FatJet_pt'+LC, 'FatJet_eta'+LC, 'FatJet_phi'+LC, 'FatJet_mass'+LC],
                    'TLVars'   :['FatJet_pt', 'FatJet_eta', 'FatJet_phi', 'FatJet_mass']},
    'ak8sj'      : ['SubJet_pt', 'SubJet_btagDeepB'],
#
    'genpvars'   : ['GenPart_pt', 'GenPart_eta', 'GenPart_phi', 'GenPart_mass', 
                    'GenPart_status', 'GenPart_pdgId', 'GenPart_genPartIdxMother','genTtbarId'], # event level identifier for ttbar+bb

    'event'      : ['MET_phi', 'MET_pt','run','luminosityBlock','event'],
    'filters_all'    : ['Flag_goodVertices','Flag_globalSuperTightHalo2016Filter','Flag_HBHENoiseFilter',
                        'Flag_HBHENoiseIsoFilter','Flag_EcalDeadCellTriggerPrimitiveFilter',
                        'Flag_BadPFMuonFilter','Flag_eeBadScFilter'],
    'filters_year' : {'2016': [], '2017':['Flag_ecalBadCalibFilterV2'], '2018':['Flag_ecalBadCalibFilterV2']},
    # these are MC only
    'sysvars_mc'      : ['genWeight','puWeight',
                         #'BTagWeight',
                         #'BTagWeight_jes_up','BTagWeight_jes_down',
                         #'BTagWeight_lf_up','BTagWeight_lf_down',
                         #'BTagWeight_hf_up','BTagWeight_hf_down',
                         #'BTagWeight_lfstats1_up','BTagWeight_lfstats1_down',
                         #'BTagWeight_lfstats2_up','BTagWeight_lfstats2_down',
                         #'BTagWeight_hfstats1_up','BTagWeight_hfstats1_down',
                         #'BTagWeight_hfstats2_up','BTagWeight_hfstats2_down',
                         'puWeightUp','puWeightDown', 
                         'pdfWeight_Up','pdfWeight_Down',],
    'sysvars_2016'    : ['PrefireWeight','PrefireWeight_Up','PrefireWeight_Down'],
    'sysvars_2017'    : ['PrefireWeight','PrefireWeight_Up','PrefireWeight_Down'],
    'sysvars_2018'    : [],
    'lheWeights'      : ['PSWeight','LHEScaleWeight','LHEReweightingWeight'],
    'dataHLT_all'     : [ 'HLT_IsoMu24' , 'HLT_IsoMu27', 'HLT_Mu50','HLT_Ele50_CaloIdVT_GsfTrkIdT_PFJet165',
                          'HLT_Ele27_WPTight_Gsf', 'HLT_Photon175','HLT_Ele115_CaloIdVT_GsfTrkIdT'],
    'dataHLT_2016'    : ['HLT_IsoTkMu24','HLT_TkMu50','HLT_Ele45_CaloIdVT_GsfTrkIdT_PFJet200_PFJet50'],
    'dataHLT_2017'    : ['HLT_Ele35_WPTight_Gsf', 'HLT_Ele32_WPTight_Gsf_L1DoubleEG', 'HLT_Photon200', 'HLT_Ele28_eta2p1_WPTight_Gsf_HT150',
                         'HLT_OldMu100','HLT_TkMu100'],
    'dataHLT_2018'    : ['HLT_Ele35_WPTight_Gsf', 'HLT_Ele32_WPTight_Gsf_L1DoubleEG', 'HLT_Photon200', 'HLT_Ele28_eta2p1_WPTight_Gsf_HT150',
                         'HLT_Ele32_WPTight_Gsf',
                         'HLT_OldMu100','HLT_TkMu100'],
    'valRCvars'  : ['ResolvedTopCandidate_discriminator', 'ResolvedTopCandidate_j1Idx', 'ResolvedTopCandidate_j2Idx', 'ResolvedTopCandidate_j3Idx'],
    'label'      : ['isTAllHad']
}

##### DNN backend for Z/H -> bb #####
dnn_ZH_dir  = dataDir+'/NN_files/'
# only event level variables
dnn_ZH_vars = [
    'max_lb_dr',
    #'max_lb_invM','best_Zh_b_invM_sd',
    'n_Zh_btag_sj', 'Zh_bbvLscore', 'outZh_max_bbvLscore',#'best_rt_score',
    'n_b_outZh','n_Zh_sj',  'Zh_bestb_sj', #'Zh_worstb_sj',
    #'Zh_eta', 'Zh_l_dr','n_q_outZh', 
    'Zh_deepB','b1_outZh_score', 'b2_outZh_score', 'Zh_b1_invM_sd', 'Zh_b2_invM_sd','Zh_l_invM_sd',
    'Zh_Wscore', 'Zh_Tscore', 'outZh_max_Wscore', 'outZh_max_Tscore', 
    'max_farl_b_q_dr',
    'ht_b', 'ht_outZh', 'min_farl_b_q_dr', 'outZh_bqq_mass', 
    'outZh_bb_dr', 'outZh_qq_dr',
    #'Zh_bqq_dr', 
    'Zh_lbbqq_dr',
    #'n_ak8_Zhbb', 
    'n_ak8jets', 'n_ak4jets',  
    'nonZhbb_b1_dr', 'nonZhbb_b2_dr', 
    #'sjpt1_over_Zhpt', 'sjpt2_over_Zhpt',
    #'Zh_bbscore_sj', 
    #'b1_over_Zhpt', 'bb_over_Zhpt',
    'spher','aplan','n_b_inZh', 'n_q_inZh']
    #'H_M',
    #'H_pt',
    #'min_lb_invm', 'MET_pt', 'b2oHZpt' 
    #'lb_mtb1', 'lb_invm1', 'lb_dr1',
    ##'weight', 'genWeight'] ####### dont do this...
old_dnn_ZH_vars = [
    'max_lb_dr','max_lb_invm', 'n_H_sj_btag', 'nJets30', 'H_score', 'best_rt_score',
    'n_qnonHbb', 'n_nonHbb', 'Hl_dr', 'n_H_sj', 'n_b_Hbb', 'H_sj_bestb', 'H_sj_worstb',
    'H_eta','H_bbscore','b1_outH_score', 'best_Wb_invM_sd', 'Hb_invM1_sd', 'Hb_invM2_sd','Hl_invm_sd',
    'H_Wscore', 'H_Tscore', 'nhbbFatJets', 'nFatJets', 'nJets', 'nonHbb_b1_dr', 'nonHbb_b2_dr', 
    'H_sj_bbscore', 
    'b1oHZpt', 'bboHZpt',
    'spher','aplan',
    #'H_M',
    #'H_pt',
    #'min_lb_invm', 'MET_pt', 'b2oHZpt' 
    #'lb_mtb1', 'lb_invm1', 'lb_dr1',
    'n_q_Hbb', 'weight', 'genWeight']
uncor_dnn_ZH_vars = [ # tests_failed >= 4 
    'min_lb_dr', 'b2_outH_score'
]
#
dnn_ZH_alpha      = 0.00003 # 200: 0.0003 # 300 : 0.00003
dnn_ZH_batch_size = 512
fl_gamma          = .2 # 200: .1    , 300: 1.5 / .4
fl_alpha          = .85 # 200: .85 , 300: .80 /.85
dnn_ZH_epochs     = 0 #210 ### 200: 120, 300: 100
DNNoutputDir      = dataDir+'/NN_files/'
DNNoutputName     = 'corr_noweight_noM.h5'
DNNmodelName      = 'corr_noweight_model_noM.h5' 
DNNuseWeights     = True
