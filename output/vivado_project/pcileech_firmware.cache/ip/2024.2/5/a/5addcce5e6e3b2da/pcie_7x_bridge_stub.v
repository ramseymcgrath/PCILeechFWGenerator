// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Jul 18 01:31:37 2025
// Host        : muttti-System-Product-Name running 64-bit Ubuntu 24.04.2 LTS
// Command     : write_verilog -force -mode synth_stub -rename_top decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix -prefix
//               decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix_ pcie_7x_bridge_stub.v
// Design      : pcie_7x_bridge
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a75tfgg484-2
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* CHECK_LICENSE_TYPE = "pcie_7x_bridge,pcie_7x_bridge_pcie2_top,{}" *) (* CORE_GENERATION_INFO = "pcie_7x_bridge,pcie_7x_bridge_pcie2_top,{x_ipProduct=Vivado 2024.2,x_ipVendor=xilinx.com,x_ipLibrary=ip,x_ipName=pcie_7x,x_ipVersion=3.3,x_ipCoreRevision=22,x_ipLanguage=VERILOG,x_ipSimLanguage=MIXED,PCIE_ID_IF=FALSE,c_component_name=pcie_7x_bridge,dev_port_type=0000,c_dev_port_type=0,c_header_type=00,c_upstream_facing=TRUE,max_lnk_wdt=000001,max_lnk_spd=1,c_gen1=false,pci_exp_int_freq=1,c_pcie_fast_config=0,bar_0=FFFFFC04,bar_1=FFFFFFFF,bar_2=00000000,bar_3=00000000,bar_4=00000000,bar_5=00000000,xrom_bar=00000000,cost_table=1,ven_id=10ec,dev_id=8125,rev_id=04,subsys_ven_id=4332,subsys_id=7,class_code=020000,cardbus_cis_ptr=00000000,cap_ver=2,c_pcie_cap_slot_implemented=FALSE,mps=010,cmps=2,ext_tag_fld_sup=FALSE,c_dev_control_ext_tag_default=FALSE,phantm_func_sup=00,c_phantom_functions=0,ep_l0s_accpt_lat=000,c_ep_l0s_accpt_lat=0,ep_l1_accpt_lat=111,c_ep_l1_accpt_lat=7,c_cpl_timeout_disable_sup=FALSE,c_cpl_timeout_range=0010,c_cpl_timeout_ranges_sup=2,c_buf_opt_bma=TRUE,c_perf_level_high=TRUE,c_tx_last_tlp=29,c_rx_ram_limit=7FF,c_fc_ph=32,c_fc_pd=437,c_fc_nph=12,c_fc_npd=24,c_fc_cplh=36,c_fc_cpld=461,c_cpl_inf=TRUE,c_cpl_infinite=TRUE,c_dll_lnk_actv_cap=FALSE,c_trgt_lnk_spd=0,c_hw_auton_spd_disable=FALSE,c_de_emph=FALSE,slot_clk=TRUE,c_rcb=0,c_root_cap_crs=FALSE,c_slot_cap_attn_butn=FALSE,c_slot_cap_attn_ind=FALSE,c_slot_cap_pwr_ctrl=FALSE,c_slot_cap_pwr_ind=FALSE,c_slot_cap_hotplug_surprise=FALSE,c_slot_cap_hotplug_cap=FALSE,c_slot_cap_mrl=FALSE,c_slot_cap_elec_interlock=FALSE,c_slot_cap_no_cmd_comp_sup=FALSE,c_slot_cap_pwr_limit_value=0,c_slot_cap_pwr_limit_scale=0,c_slot_cap_physical_slot_num=0,intx=TRUE,int_pin=1,c_msi_cap_on=TRUE,c_pm_cap_next_ptr=48,c_msi_64b_addr=TRUE,c_msi=0,c_msi_mult_msg_extn=0,c_msi_per_vctr_mask_cap=FALSE,c_msix_cap_on=TRUE,c_msix_next_ptr=00,c_pcie_cap_next_ptr=9C,c_msix_table_size=000,c_msix_table_offset=0,c_msix_table_bir=0,c_msix_pba_offset=0,c_msix_pba_bir=0,dsi=0,c_dsi_bool=FALSE,d1_sup=0,c_d1_support=FALSE,d2_sup=0,c_d2_support=FALSE,pme_sup=0F,c_pme_support=0F,no_soft_rst=TRUE,pwr_con_d0_state=00,con_scl_fctr_d0_state=0,pwr_con_d1_state=00,con_scl_fctr_d1_state=0,pwr_con_d2_state=00,con_scl_fctr_d2_state=0,pwr_con_d3_state=00,con_scl_fctr_d3_state=0,pwr_dis_d0_state=00,dis_scl_fctr_d0_state=0,pwr_dis_d1_state=00,dis_scl_fctr_d1_state=0,pwr_dis_d2_state=00,dis_scl_fctr_d2_state=0,pwr_dis_d3_state=00,dis_scl_fctr_d3_state=0,c_dsn_cap_enabled=TRUE,c_dsn_base_ptr=100,c_vc_cap_enabled=FALSE,c_vc_base_ptr=000,c_vc_cap_reject_snoop=FALSE,c_vsec_cap_enabled=FALSE,c_vsec_base_ptr=000,c_vsec_next_ptr=000,c_dsn_next_ptr=000,c_vc_next_ptr=000,c_pci_cfg_space_addr=3F,c_ext_pci_cfg_space_addr=3FF,c_last_cfg_dw=10C,c_enable_msg_route=00000000000,bram_lat=0,c_rx_raddr_lat=0,c_rx_rdata_lat=2,c_rx_write_lat=0,c_tx_raddr_lat=0,c_tx_rdata_lat=2,c_tx_write_lat=0,c_ll_ack_timeout_enable=FALSE,c_ll_ack_timeout_function=0,c_ll_ack_timeout=0000,c_ll_replay_timeout_enable=FALSE,c_ll_replay_timeout_func=1,c_ll_replay_timeout=0000,c_dis_lane_reverse=TRUE,c_upconfig_capable=TRUE,c_disable_scrambling=FALSE,c_disable_tx_aspm_l0s=FALSE,c_pcie_dbg_ports=TRUE,pci_exp_ref_freq=0,c_xlnx_ref_board=NONE,c_pcie_blk_locn=0,c_ur_atomic=FALSE,c_dev_cap2_atomicop32_completer_supported=FALSE,c_dev_cap2_atomicop64_completer_supported=FALSE,c_dev_cap2_cas128_completer_supported=FALSE,c_dev_cap2_tph_completer_supported=00,c_dev_cap2_ari_forwarding_supported=FALSE,c_dev_cap2_atomicop_routing_supported=FALSE,c_link_cap_aspm_optionality=FALSE,c_aer_cap_on=FALSE,c_aer_base_ptr=000,c_aer_cap_nextptr=000,c_aer_cap_ecrc_check_capable=FALSE,c_aer_cap_ecrc_gen_capable=FALSE,c_aer_cap_multiheader=FALSE,c_aer_cap_permit_rooterr_update=FALSE,c_rbar_cap_on=FALSE,c_rbar_base_ptr=000,c_rbar_cap_nextptr=000,c_rbar_num=0,c_rbar_cap_sup0=00001,c_rbar_cap_index0=0,c_rbar_cap_control_encodedbar0=00,c_rbar_cap_sup1=00001,c_rbar_cap_index1=0,c_rbar_cap_control_encodedbar1=00,c_rbar_cap_sup2=00001,c_rbar_cap_index2=0,c_rbar_cap_control_encodedbar2=00,c_rbar_cap_sup3=00001,c_rbar_cap_index3=0,c_rbar_cap_control_encodedbar3=00,c_rbar_cap_sup4=00001,c_rbar_cap_index4=0,c_rbar_cap_control_encodedbar4=00,c_rbar_cap_sup5=00001,c_rbar_cap_index5=0,c_rbar_cap_control_encodedbar5=00,c_recrc_check=0,c_recrc_check_trim=FALSE,c_disable_rx_poisoned_resp=FALSE,c_trn_np_fc=TRUE,c_ur_inv_req=TRUE,c_ur_prs_response=TRUE,c_silicon_rev=2,c_aer_cap_optional_err_support=000000,LINK_CAP_MAX_LINK_WIDTH=1,C_DATA_WIDTH=64,PIPE_SIM=FALSE,PCIE_EXT_CLK=TRUE,PCIE_EXT_GT_COMMON=FALSE,EXT_CH_GT_DRP=FALSE,TRANSCEIVER_CTRL_STATUS_PORTS=FALSE,SHARED_LOGIC_IN_CORE=FALSE,ERR_REPORTING_IF=TRUE,PL_INTERFACE=TRUE,CFG_MGMT_IF=TRUE,CFG_CTL_IF=TRUE,CFG_STATUS_IF=TRUE,RCV_MSG_IF=TRUE,CFG_FC_IF=TRUE,EXT_PIPE_INTERFACE=FALSE,EXT_STARTUP_PRIMITIVE=FALSE,KEEP_WIDTH=8,PCIE_ASYNC_EN=FALSE,ENABLE_JTAG_DBG=FALSE,REDUCE_OOB_FREQ=FALSE}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* X_CORE_INFO = "pcie_7x_bridge_pcie2_top,Vivado 2024.2" *) 
module decalper_eb_ot_sdeen_pot_pi_dehcac_xnilix(pci_exp_txp, pci_exp_txn, pci_exp_rxp, 
  pci_exp_rxn, pipe_pclk_in, pipe_rxusrclk_in, pipe_rxoutclk_in, pipe_dclk_in, 
  pipe_userclk1_in, pipe_userclk2_in, pipe_oobclk_in, pipe_mmcm_lock_in, pipe_txoutclk_out, 
  pipe_rxoutclk_out, pipe_pclk_sel_out, pipe_gen3_out, user_clk_out, user_reset_out, 
  user_lnk_up, user_app_rdy, tx_buf_av, tx_cfg_req, tx_err_drop, s_axis_tx_tready, 
  s_axis_tx_tdata, s_axis_tx_tkeep, s_axis_tx_tlast, s_axis_tx_tvalid, s_axis_tx_tuser, 
  tx_cfg_gnt, m_axis_rx_tdata, m_axis_rx_tkeep, m_axis_rx_tlast, m_axis_rx_tvalid, 
  m_axis_rx_tready, m_axis_rx_tuser, rx_np_ok, rx_np_req, fc_cpld, fc_cplh, fc_npd, fc_nph, fc_pd, 
  fc_ph, fc_sel, cfg_mgmt_do, cfg_mgmt_rd_wr_done, cfg_status, cfg_command, cfg_dstatus, 
  cfg_dcommand, cfg_lstatus, cfg_lcommand, cfg_dcommand2, cfg_pcie_link_state, 
  cfg_pmcsr_pme_en, cfg_pmcsr_powerstate, cfg_pmcsr_pme_status, 
  cfg_received_func_lvl_rst, cfg_mgmt_di, cfg_mgmt_byte_en, cfg_mgmt_dwaddr, 
  cfg_mgmt_wr_en, cfg_mgmt_rd_en, cfg_mgmt_wr_readonly, cfg_err_ecrc, cfg_err_ur, 
  cfg_err_cpl_timeout, cfg_err_cpl_unexpect, cfg_err_cpl_abort, cfg_err_posted, 
  cfg_err_cor, cfg_err_atomic_egress_blocked, cfg_err_internal_cor, cfg_err_malformed, 
  cfg_err_mc_blocked, cfg_err_poisoned, cfg_err_norecovery, cfg_err_tlp_cpl_header, 
  cfg_err_cpl_rdy, cfg_err_locked, cfg_err_acs, cfg_err_internal_uncor, cfg_trn_pending, 
  cfg_pm_halt_aspm_l0s, cfg_pm_halt_aspm_l1, cfg_pm_force_state_en, cfg_pm_force_state, 
  cfg_dsn, cfg_interrupt, cfg_interrupt_rdy, cfg_interrupt_assert, cfg_interrupt_di, 
  cfg_interrupt_do, cfg_interrupt_mmenable, cfg_interrupt_msienable, 
  cfg_interrupt_msixenable, cfg_interrupt_msixfm, cfg_interrupt_stat, 
  cfg_pciecap_interrupt_msgnum, cfg_to_turnoff, cfg_turnoff_ok, cfg_bus_number, 
  cfg_device_number, cfg_function_number, cfg_pm_wake, cfg_pm_send_pme_to, 
  cfg_ds_bus_number, cfg_ds_device_number, cfg_ds_function_number, 
  cfg_mgmt_wr_rw1c_as_rw, cfg_msg_received, cfg_msg_data, cfg_bridge_serr_en, 
  cfg_slot_control_electromech_il_ctl_pulse, cfg_root_control_syserr_corr_err_en, 
  cfg_root_control_syserr_non_fatal_err_en, cfg_root_control_syserr_fatal_err_en, 
  cfg_root_control_pme_int_en, cfg_aer_rooterr_corr_err_reporting_en, 
  cfg_aer_rooterr_non_fatal_err_reporting_en, cfg_aer_rooterr_fatal_err_reporting_en, 
  cfg_aer_rooterr_corr_err_received, cfg_aer_rooterr_non_fatal_err_received, 
  cfg_aer_rooterr_fatal_err_received, cfg_msg_received_err_cor, 
  cfg_msg_received_err_non_fatal, cfg_msg_received_err_fatal, 
  cfg_msg_received_pm_as_nak, cfg_msg_received_pm_pme, cfg_msg_received_pme_to_ack, 
  cfg_msg_received_assert_int_a, cfg_msg_received_assert_int_b, 
  cfg_msg_received_assert_int_c, cfg_msg_received_assert_int_d, 
  cfg_msg_received_deassert_int_a, cfg_msg_received_deassert_int_b, 
  cfg_msg_received_deassert_int_c, cfg_msg_received_deassert_int_d, 
  cfg_msg_received_setslotpowerlimit, pl_directed_link_change, pl_directed_link_width, 
  pl_directed_link_speed, pl_directed_link_auton, pl_upstream_prefer_deemph, 
  pl_sel_lnk_rate, pl_sel_lnk_width, pl_ltssm_state, pl_lane_reversal_mode, pl_phy_lnk_up, 
  pl_tx_pm_state, pl_rx_pm_state, pl_link_upcfg_cap, pl_link_gen2_cap, 
  pl_link_partner_gen2_supported, pl_initial_link_width, pl_directed_change_done, 
  pl_received_hot_rst, pl_transmit_hot_rst, pl_downstream_deemph_source, 
  cfg_err_aer_headerlog, cfg_aer_interrupt_msgnum, cfg_err_aer_headerlog_set, 
  cfg_aer_ecrc_check_en, cfg_aer_ecrc_gen_en, cfg_vc_tcvc_map, sys_clk, sys_rst_n, 
  pipe_mmcm_rst_n, pcie_drp_clk, pcie_drp_en, pcie_drp_we, pcie_drp_addr, pcie_drp_di, 
  pcie_drp_do, pcie_drp_rdy)
/* synthesis syn_black_box black_box_pad_pin="pci_exp_txp[0:0],pci_exp_txn[0:0],pci_exp_rxp[0:0],pci_exp_rxn[0:0],pipe_rxoutclk_in[0:0],pipe_mmcm_lock_in,pipe_txoutclk_out,pipe_rxoutclk_out[0:0],pipe_pclk_sel_out[0:0],pipe_gen3_out,user_reset_out,user_lnk_up,user_app_rdy,tx_buf_av[5:0],tx_cfg_req,tx_err_drop,s_axis_tx_tready,s_axis_tx_tdata[63:0],s_axis_tx_tkeep[7:0],s_axis_tx_tlast,s_axis_tx_tvalid,s_axis_tx_tuser[3:0],tx_cfg_gnt,m_axis_rx_tdata[63:0],m_axis_rx_tkeep[7:0],m_axis_rx_tlast,m_axis_rx_tvalid,m_axis_rx_tready,m_axis_rx_tuser[21:0],rx_np_ok,rx_np_req,fc_cpld[11:0],fc_cplh[7:0],fc_npd[11:0],fc_nph[7:0],fc_pd[11:0],fc_ph[7:0],fc_sel[2:0],cfg_mgmt_do[31:0],cfg_mgmt_rd_wr_done,cfg_status[15:0],cfg_command[15:0],cfg_dstatus[15:0],cfg_dcommand[15:0],cfg_lstatus[15:0],cfg_lcommand[15:0],cfg_dcommand2[15:0],cfg_pcie_link_state[2:0],cfg_pmcsr_pme_en,cfg_pmcsr_powerstate[1:0],cfg_pmcsr_pme_status,cfg_received_func_lvl_rst,cfg_mgmt_di[31:0],cfg_mgmt_byte_en[3:0],cfg_mgmt_dwaddr[9:0],cfg_mgmt_wr_en,cfg_mgmt_rd_en,cfg_mgmt_wr_readonly,cfg_err_ecrc,cfg_err_ur,cfg_err_cpl_timeout,cfg_err_cpl_unexpect,cfg_err_cpl_abort,cfg_err_posted,cfg_err_cor,cfg_err_atomic_egress_blocked,cfg_err_internal_cor,cfg_err_malformed,cfg_err_mc_blocked,cfg_err_poisoned,cfg_err_norecovery,cfg_err_tlp_cpl_header[47:0],cfg_err_cpl_rdy,cfg_err_locked,cfg_err_acs,cfg_err_internal_uncor,cfg_trn_pending,cfg_pm_halt_aspm_l0s,cfg_pm_halt_aspm_l1,cfg_pm_force_state_en,cfg_pm_force_state[1:0],cfg_dsn[63:0],cfg_interrupt,cfg_interrupt_rdy,cfg_interrupt_assert,cfg_interrupt_di[7:0],cfg_interrupt_do[7:0],cfg_interrupt_mmenable[2:0],cfg_interrupt_msienable,cfg_interrupt_msixenable,cfg_interrupt_msixfm,cfg_interrupt_stat,cfg_pciecap_interrupt_msgnum[4:0],cfg_to_turnoff,cfg_turnoff_ok,cfg_bus_number[7:0],cfg_device_number[4:0],cfg_function_number[2:0],cfg_pm_wake,cfg_pm_send_pme_to,cfg_ds_bus_number[7:0],cfg_ds_device_number[4:0],cfg_ds_function_number[2:0],cfg_mgmt_wr_rw1c_as_rw,cfg_msg_received,cfg_msg_data[15:0],cfg_bridge_serr_en,cfg_slot_control_electromech_il_ctl_pulse,cfg_root_control_syserr_corr_err_en,cfg_root_control_syserr_non_fatal_err_en,cfg_root_control_syserr_fatal_err_en,cfg_root_control_pme_int_en,cfg_aer_rooterr_corr_err_reporting_en,cfg_aer_rooterr_non_fatal_err_reporting_en,cfg_aer_rooterr_fatal_err_reporting_en,cfg_aer_rooterr_corr_err_received,cfg_aer_rooterr_non_fatal_err_received,cfg_aer_rooterr_fatal_err_received,cfg_msg_received_err_cor,cfg_msg_received_err_non_fatal,cfg_msg_received_err_fatal,cfg_msg_received_pm_as_nak,cfg_msg_received_pm_pme,cfg_msg_received_pme_to_ack,cfg_msg_received_assert_int_a,cfg_msg_received_assert_int_b,cfg_msg_received_assert_int_c,cfg_msg_received_assert_int_d,cfg_msg_received_deassert_int_a,cfg_msg_received_deassert_int_b,cfg_msg_received_deassert_int_c,cfg_msg_received_deassert_int_d,cfg_msg_received_setslotpowerlimit,pl_directed_link_change[1:0],pl_directed_link_width[1:0],pl_directed_link_speed,pl_directed_link_auton,pl_upstream_prefer_deemph,pl_sel_lnk_rate,pl_sel_lnk_width[1:0],pl_ltssm_state[5:0],pl_lane_reversal_mode[1:0],pl_phy_lnk_up,pl_tx_pm_state[2:0],pl_rx_pm_state[1:0],pl_link_upcfg_cap,pl_link_gen2_cap,pl_link_partner_gen2_supported,pl_initial_link_width[2:0],pl_directed_change_done,pl_received_hot_rst,pl_transmit_hot_rst,pl_downstream_deemph_source,cfg_err_aer_headerlog[127:0],cfg_aer_interrupt_msgnum[4:0],cfg_err_aer_headerlog_set,cfg_aer_ecrc_check_en,cfg_aer_ecrc_gen_en,cfg_vc_tcvc_map[6:0],sys_rst_n,pipe_mmcm_rst_n,pcie_drp_en,pcie_drp_we,pcie_drp_addr[8:0],pcie_drp_di[15:0],pcie_drp_do[15:0],pcie_drp_rdy" */
/* synthesis syn_force_seq_prim="pipe_pclk_in" */
/* synthesis syn_force_seq_prim="pipe_rxusrclk_in" */
/* synthesis syn_force_seq_prim="pipe_dclk_in" */
/* synthesis syn_force_seq_prim="pipe_userclk1_in" */
/* synthesis syn_force_seq_prim="pipe_userclk2_in" */
/* synthesis syn_force_seq_prim="pipe_oobclk_in" */
/* synthesis syn_force_seq_prim="user_clk_out" */
/* synthesis syn_force_seq_prim="sys_clk" */
/* synthesis syn_force_seq_prim="pcie_drp_clk" */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txp" *) (* X_INTERFACE_MODE = "master" *) output [0:0]pci_exp_txp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txn" *) output [0:0]pci_exp_txn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxp" *) input [0:0]pci_exp_rxp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxn" *) input [0:0]pci_exp_rxn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_in" *) (* X_INTERFACE_MODE = "slave" *) input pipe_pclk_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxusrclk_in" *) input pipe_rxusrclk_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_in" *) input [0:0]pipe_rxoutclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock dclk_in" *) input pipe_dclk_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk1_in" *) input pipe_userclk1_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk2_in" *) input pipe_userclk2_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock oobclk_in" *) input pipe_oobclk_in /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_lock_in" *) input pipe_mmcm_lock_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock txoutclk_out" *) output pipe_txoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_out" *) output [0:0]pipe_rxoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_sel_out" *) output [0:0]pipe_pclk_sel_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock gen3_out" *) output pipe_gen3_out;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.user_clk_out CLK" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.user_clk_out, ASSOCIATED_BUSIF m_axis_rx:s_axis_tx, FREQ_HZ 125000000, ASSOCIATED_RESET user_reset_out, FREQ_TOLERANCE_HZ 0, PHASE 0.0, INSERT_VIP 0" *) output user_clk_out /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 RST.user_reset_out RST" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME RST.user_reset_out, POLARITY ACTIVE_HIGH, INSERT_VIP 0" *) output user_reset_out;
  output user_lnk_up;
  output user_app_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_buf_av" *) (* X_INTERFACE_MODE = "master" *) output [5:0]tx_buf_av;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_cfg_req" *) output tx_cfg_req;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_err_drop" *) output tx_err_drop;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TREADY" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME s_axis_tx, TDATA_NUM_BYTES 8, TDEST_WIDTH 0, TID_WIDTH 0, TUSER_WIDTH 4, HAS_TREADY 1, HAS_TSTRB 0, HAS_TKEEP 1, HAS_TLAST 1, FREQ_HZ 100000000, PHASE 0.0, LAYERED_METADATA undef, INSERT_VIP 0" *) output s_axis_tx_tready;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TDATA" *) input [63:0]s_axis_tx_tdata;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TKEEP" *) input [7:0]s_axis_tx_tkeep;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TLAST" *) input s_axis_tx_tlast;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TVALID" *) input s_axis_tx_tvalid;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TUSER" *) input [3:0]s_axis_tx_tuser;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control tx_cfg_gnt" *) (* X_INTERFACE_MODE = "slave" *) input tx_cfg_gnt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TDATA" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME m_axis_rx, TDATA_NUM_BYTES 8, TDEST_WIDTH 0, TID_WIDTH 0, TUSER_WIDTH 22, HAS_TREADY 1, HAS_TSTRB 0, HAS_TKEEP 1, HAS_TLAST 1, FREQ_HZ 100000000, PHASE 0.0, LAYERED_METADATA undef, INSERT_VIP 0" *) output [63:0]m_axis_rx_tdata;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TKEEP" *) output [7:0]m_axis_rx_tkeep;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TLAST" *) output m_axis_rx_tlast;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TVALID" *) output m_axis_rx_tvalid;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TREADY" *) input m_axis_rx_tready;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TUSER" *) output [21:0]m_axis_rx_tuser;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control rx_np_ok" *) input rx_np_ok;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control rx_np_req" *) input rx_np_req;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc CPLD" *) (* X_INTERFACE_MODE = "master" *) output [11:0]fc_cpld;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc CPLH" *) output [7:0]fc_cplh;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc NPD" *) output [11:0]fc_npd;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc NPH" *) output [7:0]fc_nph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc PD" *) output [11:0]fc_pd;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc PH" *) output [7:0]fc_ph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc SEL" *) input [2:0]fc_sel;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_DATA" *) (* X_INTERFACE_MODE = "slave" *) output [31:0]cfg_mgmt_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_WRITE_DONE" *) output cfg_mgmt_rd_wr_done;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status status" *) output [15:0]cfg_status;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status command" *) output [15:0]cfg_command;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dstatus" *) output [15:0]cfg_dstatus;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dcommand" *) output [15:0]cfg_dcommand;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status lstatus" *) output [15:0]cfg_lstatus;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status lcommand" *) output [15:0]cfg_lcommand;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dcommand2" *) output [15:0]cfg_dcommand2;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pcie_link_state" *) output [2:0]cfg_pcie_link_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_pme_en" *) output cfg_pmcsr_pme_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_powerstate" *) output [1:0]cfg_pmcsr_powerstate;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_pme_status" *) output cfg_pmcsr_pme_status;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status received_func_lvl_rst" *) output cfg_received_func_lvl_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt WRITE_DATA" *) input [31:0]cfg_mgmt_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt BYTE_EN" *) input [3:0]cfg_mgmt_byte_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt ADDR" *) input [9:0]cfg_mgmt_dwaddr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt WRITE_EN" *) input cfg_mgmt_wr_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_EN" *) input cfg_mgmt_rd_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READONLY" *) input cfg_mgmt_wr_readonly;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err ecrc" *) (* X_INTERFACE_MODE = "slave" *) input cfg_err_ecrc;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err ur" *) input cfg_err_ur;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_timeout" *) input cfg_err_cpl_timeout;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_unexpect" *) input cfg_err_cpl_unexpect;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_abort" *) input cfg_err_cpl_abort;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err posted" *) input cfg_err_posted;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cor" *) input cfg_err_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err atomic_egress_blocked" *) input cfg_err_atomic_egress_blocked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err internal_cor" *) input cfg_err_internal_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err malformed" *) input cfg_err_malformed;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err mc_blocked" *) input cfg_err_mc_blocked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err poisoned" *) input cfg_err_poisoned;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err norecovery" *) input cfg_err_norecovery;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err tlp_cpl_header" *) input [47:0]cfg_err_tlp_cpl_header;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_rdy" *) output cfg_err_cpl_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err locked" *) input cfg_err_locked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err acs" *) input cfg_err_acs;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err internal_uncor" *) input cfg_err_internal_uncor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control trn_pending" *) input cfg_trn_pending;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_halt_aspm_l0s" *) input cfg_pm_halt_aspm_l0s;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_halt_aspm_l1" *) input cfg_pm_halt_aspm_l1;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_force_state_en" *) input cfg_pm_force_state_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_force_state" *) input [1:0]cfg_pm_force_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control dsn" *) input [63:0]cfg_dsn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt interrupt" *) (* X_INTERFACE_MODE = "slave" *) input cfg_interrupt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt rdy" *) output cfg_interrupt_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt assert" *) input cfg_interrupt_assert;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt write_data" *) input [7:0]cfg_interrupt_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt read_data" *) output [7:0]cfg_interrupt_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt mmenable" *) output [2:0]cfg_interrupt_mmenable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msienable" *) output cfg_interrupt_msienable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msixenable" *) output cfg_interrupt_msixenable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msixfm" *) output cfg_interrupt_msixfm;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt stat" *) input cfg_interrupt_stat;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt pciecap_interrupt_msgnum" *) input [4:0]cfg_pciecap_interrupt_msgnum;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status turnoff" *) output cfg_to_turnoff;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control turnoff_ok" *) input cfg_turnoff_ok;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status bus_number" *) output [7:0]cfg_bus_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status device_number" *) output [4:0]cfg_device_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status function_number" *) output [2:0]cfg_function_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_wake" *) input cfg_pm_wake;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_send_pme_to" *) input cfg_pm_send_pme_to;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_bus_number" *) input [7:0]cfg_ds_bus_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_device_number" *) input [4:0]cfg_ds_device_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_function_number" *) input [2:0]cfg_ds_function_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt TYPE1_CFG_REG_ACCESS" *) input cfg_mgmt_wr_rw1c_as_rw;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received" *) (* X_INTERFACE_MODE = "master" *) output cfg_msg_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd data" *) output [15:0]cfg_msg_data;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status bridge_serr_en" *) output cfg_bridge_serr_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status slot_control_electromech_il_ctl_pulse" *) output cfg_slot_control_electromech_il_ctl_pulse;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_corr_err_en" *) output cfg_root_control_syserr_corr_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_non_fatal_err_en" *) output cfg_root_control_syserr_non_fatal_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_fatal_err_en" *) output cfg_root_control_syserr_fatal_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_pme_int_en" *) output cfg_root_control_pme_int_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_corr_err_reporting_en" *) output cfg_aer_rooterr_corr_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_non_fatal_err_reporting_en" *) output cfg_aer_rooterr_non_fatal_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_fatal_err_reporting_en" *) output cfg_aer_rooterr_fatal_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_corr_err_received" *) output cfg_aer_rooterr_corr_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_non_fatal_err_received" *) output cfg_aer_rooterr_non_fatal_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_fatal_err_received" *) output cfg_aer_rooterr_fatal_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_cor" *) output cfg_msg_received_err_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_non_fatal" *) output cfg_msg_received_err_non_fatal;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_fatal" *) output cfg_msg_received_err_fatal;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received_pm_as_nak" *) output cfg_msg_received_pm_as_nak;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd pm_pme" *) output cfg_msg_received_pm_pme;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd pme_to_ack" *) output cfg_msg_received_pme_to_ack;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_a" *) output cfg_msg_received_assert_int_a;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_b" *) output cfg_msg_received_assert_int_b;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_c" *) output cfg_msg_received_assert_int_c;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_d" *) output cfg_msg_received_assert_int_d;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_a" *) output cfg_msg_received_deassert_int_a;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_b" *) output cfg_msg_received_deassert_int_b;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_c" *) output cfg_msg_received_deassert_int_c;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_d" *) output cfg_msg_received_deassert_int_d;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received_setslotpowerlimit" *) output cfg_msg_received_setslotpowerlimit;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_change" *) (* X_INTERFACE_MODE = "slave" *) input [1:0]pl_directed_link_change;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_width" *) input [1:0]pl_directed_link_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_speed" *) input pl_directed_link_speed;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_auton" *) input pl_directed_link_auton;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl upstream_prefer_deemph" *) input pl_upstream_prefer_deemph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl sel_lnk_rate" *) output pl_sel_lnk_rate;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl sel_lnk_width" *) output [1:0]pl_sel_lnk_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl ltssm_state" *) output [5:0]pl_ltssm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl lane_reversal_mode" *) output [1:0]pl_lane_reversal_mode;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl phy_lnk_up" *) output pl_phy_lnk_up;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl tx_pm_state" *) output [2:0]pl_tx_pm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl rx_pm_state" *) output [1:0]pl_rx_pm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_upcfg_cap" *) output pl_link_upcfg_cap;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_gen2_cap" *) output pl_link_gen2_cap;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_partner_gen2_supported" *) output pl_link_partner_gen2_supported;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl initial_link_width" *) output [2:0]pl_initial_link_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_change_done" *) output pl_directed_change_done;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl received_hot_rst" *) output pl_received_hot_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl transmit_hot_rst" *) input pl_transmit_hot_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl downstream_deemph_source" *) input pl_downstream_deemph_source;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err err_aer_headerlog" *) input [127:0]cfg_err_aer_headerlog;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_interrupt_msgnum" *) input [4:0]cfg_aer_interrupt_msgnum;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err err_aer_headerlog_set" *) output cfg_err_aer_headerlog_set;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_ecrc_check_en" *) output cfg_aer_ecrc_check_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_ecrc_gen_en" *) output cfg_aer_ecrc_gen_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status vc_tcvc_map" *) output [6:0]cfg_vc_tcvc_map;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.sys_clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.sys_clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, INSERT_VIP 0" *) input sys_clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 RST.sys_rst_n RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME RST.sys_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input sys_rst_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_rst_n" *) input pipe_mmcm_rst_n;
  input pcie_drp_clk /* synthesis syn_isclock = 1 */;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DEN" *) (* X_INTERFACE_MODE = "slave" *) input pcie_drp_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DWE" *) input pcie_drp_we;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DADDR" *) input [8:0]pcie_drp_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DI" *) input [15:0]pcie_drp_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DO" *) output [15:0]pcie_drp_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DRDY" *) output pcie_drp_rdy;
endmodule
