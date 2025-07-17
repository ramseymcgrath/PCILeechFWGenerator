// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2025 Advanced Micro Devices, Inc. All Rights Reserved.
// -------------------------------------------------------------------------------

`timescale 1 ps / 1 ps

(* BLOCK_STUB = "true" *)
module pcie_7x_bridge (
  pci_exp_txp,
  pci_exp_txn,
  pci_exp_rxp,
  pci_exp_rxn,
  pipe_pclk_in,
  pipe_rxusrclk_in,
  pipe_rxoutclk_in,
  pipe_dclk_in,
  pipe_userclk1_in,
  pipe_userclk2_in,
  pipe_oobclk_in,
  pipe_mmcm_lock_in,
  pipe_txoutclk_out,
  pipe_rxoutclk_out,
  pipe_pclk_sel_out,
  pipe_gen3_out,
  user_clk_out,
  user_reset_out,
  user_lnk_up,
  user_app_rdy,
  tx_buf_av,
  tx_cfg_req,
  tx_err_drop,
  s_axis_tx_tready,
  s_axis_tx_tdata,
  s_axis_tx_tkeep,
  s_axis_tx_tlast,
  s_axis_tx_tvalid,
  s_axis_tx_tuser,
  tx_cfg_gnt,
  m_axis_rx_tdata,
  m_axis_rx_tkeep,
  m_axis_rx_tlast,
  m_axis_rx_tvalid,
  m_axis_rx_tready,
  m_axis_rx_tuser,
  rx_np_ok,
  rx_np_req,
  fc_cpld,
  fc_cplh,
  fc_npd,
  fc_nph,
  fc_pd,
  fc_ph,
  fc_sel,
  cfg_mgmt_do,
  cfg_mgmt_rd_wr_done,
  cfg_status,
  cfg_command,
  cfg_dstatus,
  cfg_dcommand,
  cfg_lstatus,
  cfg_lcommand,
  cfg_dcommand2,
  cfg_pcie_link_state,
  cfg_pmcsr_pme_en,
  cfg_pmcsr_powerstate,
  cfg_pmcsr_pme_status,
  cfg_received_func_lvl_rst,
  cfg_mgmt_di,
  cfg_mgmt_byte_en,
  cfg_mgmt_dwaddr,
  cfg_mgmt_wr_en,
  cfg_mgmt_rd_en,
  cfg_mgmt_wr_readonly,
  cfg_err_ecrc,
  cfg_err_ur,
  cfg_err_cpl_timeout,
  cfg_err_cpl_unexpect,
  cfg_err_cpl_abort,
  cfg_err_posted,
  cfg_err_cor,
  cfg_err_atomic_egress_blocked,
  cfg_err_internal_cor,
  cfg_err_malformed,
  cfg_err_mc_blocked,
  cfg_err_poisoned,
  cfg_err_norecovery,
  cfg_err_tlp_cpl_header,
  cfg_err_cpl_rdy,
  cfg_err_locked,
  cfg_err_acs,
  cfg_err_internal_uncor,
  cfg_trn_pending,
  cfg_pm_halt_aspm_l0s,
  cfg_pm_halt_aspm_l1,
  cfg_pm_force_state_en,
  cfg_pm_force_state,
  cfg_dsn,
  cfg_interrupt,
  cfg_interrupt_rdy,
  cfg_interrupt_assert,
  cfg_interrupt_di,
  cfg_interrupt_do,
  cfg_interrupt_mmenable,
  cfg_interrupt_msienable,
  cfg_interrupt_msixenable,
  cfg_interrupt_msixfm,
  cfg_interrupt_stat,
  cfg_pciecap_interrupt_msgnum,
  cfg_to_turnoff,
  cfg_turnoff_ok,
  cfg_bus_number,
  cfg_device_number,
  cfg_function_number,
  cfg_pm_wake,
  cfg_pm_send_pme_to,
  cfg_ds_bus_number,
  cfg_ds_device_number,
  cfg_ds_function_number,
  cfg_mgmt_wr_rw1c_as_rw,
  cfg_msg_received,
  cfg_msg_data,
  cfg_bridge_serr_en,
  cfg_slot_control_electromech_il_ctl_pulse,
  cfg_root_control_syserr_corr_err_en,
  cfg_root_control_syserr_non_fatal_err_en,
  cfg_root_control_syserr_fatal_err_en,
  cfg_root_control_pme_int_en,
  cfg_aer_rooterr_corr_err_reporting_en,
  cfg_aer_rooterr_non_fatal_err_reporting_en,
  cfg_aer_rooterr_fatal_err_reporting_en,
  cfg_aer_rooterr_corr_err_received,
  cfg_aer_rooterr_non_fatal_err_received,
  cfg_aer_rooterr_fatal_err_received,
  cfg_msg_received_err_cor,
  cfg_msg_received_err_non_fatal,
  cfg_msg_received_err_fatal,
  cfg_msg_received_pm_as_nak,
  cfg_msg_received_pm_pme,
  cfg_msg_received_pme_to_ack,
  cfg_msg_received_assert_int_a,
  cfg_msg_received_assert_int_b,
  cfg_msg_received_assert_int_c,
  cfg_msg_received_assert_int_d,
  cfg_msg_received_deassert_int_a,
  cfg_msg_received_deassert_int_b,
  cfg_msg_received_deassert_int_c,
  cfg_msg_received_deassert_int_d,
  cfg_msg_received_setslotpowerlimit,
  pl_directed_link_change,
  pl_directed_link_width,
  pl_directed_link_speed,
  pl_directed_link_auton,
  pl_upstream_prefer_deemph,
  pl_sel_lnk_rate,
  pl_sel_lnk_width,
  pl_ltssm_state,
  pl_lane_reversal_mode,
  pl_phy_lnk_up,
  pl_tx_pm_state,
  pl_rx_pm_state,
  pl_link_upcfg_cap,
  pl_link_gen2_cap,
  pl_link_partner_gen2_supported,
  pl_initial_link_width,
  pl_directed_change_done,
  pl_received_hot_rst,
  pl_transmit_hot_rst,
  pl_downstream_deemph_source,
  cfg_err_aer_headerlog,
  cfg_aer_interrupt_msgnum,
  cfg_err_aer_headerlog_set,
  cfg_aer_ecrc_check_en,
  cfg_aer_ecrc_gen_en,
  cfg_vc_tcvc_map,
  sys_clk,
  sys_rst_n,
  pipe_mmcm_rst_n,
  pcie_drp_clk,
  pcie_drp_en,
  pcie_drp_we,
  pcie_drp_addr,
  pcie_drp_di,
  pcie_drp_do,
  pcie_drp_rdy
);

  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txp" *)
  (* X_INTERFACE_MODE = "master pcie_7x_mgt" *)
  output [0:0]pci_exp_txp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txn" *)
  output [0:0]pci_exp_txn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxp" *)
  input [0:0]pci_exp_rxp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxn" *)
  input [0:0]pci_exp_rxn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_in" *)
  (* X_INTERFACE_MODE = "slave pipe_clock" *)
  input pipe_pclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxusrclk_in" *)
  input pipe_rxusrclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_in" *)
  input [0:0]pipe_rxoutclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock dclk_in" *)
  input pipe_dclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk1_in" *)
  input pipe_userclk1_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk2_in" *)
  input pipe_userclk2_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock oobclk_in" *)
  input pipe_oobclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_lock_in" *)
  input pipe_mmcm_lock_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock txoutclk_out" *)
  output pipe_txoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_out" *)
  output [0:0]pipe_rxoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_sel_out" *)
  output [0:0]pipe_pclk_sel_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock gen3_out" *)
  output pipe_gen3_out;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.user_clk_out CLK" *)
  (* X_INTERFACE_MODE = "master CLK.user_clk_out" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.user_clk_out, ASSOCIATED_BUSIF m_axis_rx:s_axis_tx, FREQ_HZ 125000000, ASSOCIATED_RESET user_reset_out, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN , ASSOCIATED_PORT , INSERT_VIP 0" *)
  output user_clk_out;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 RST.user_reset_out RST" *)
  (* X_INTERFACE_MODE = "master RST.user_reset_out" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME RST.user_reset_out, POLARITY ACTIVE_HIGH, INSERT_VIP 0" *)
  output user_reset_out;
  (* X_INTERFACE_IGNORE = "true" *)
  output user_lnk_up;
  (* X_INTERFACE_IGNORE = "true" *)
  output user_app_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_buf_av" *)
  (* X_INTERFACE_MODE = "master pcie2_cfg_status" *)
  output [5:0]tx_buf_av;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_cfg_req" *)
  output tx_cfg_req;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status tx_err_drop" *)
  output tx_err_drop;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TREADY" *)
  (* X_INTERFACE_MODE = "slave s_axis_tx" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME s_axis_tx, TDATA_NUM_BYTES 8, TDEST_WIDTH 0, TID_WIDTH 0, TUSER_WIDTH 4, HAS_TREADY 1, HAS_TSTRB 0, HAS_TKEEP 1, HAS_TLAST 1, FREQ_HZ 100000000, PHASE 0.0, CLK_DOMAIN , LAYERED_METADATA undef, INSERT_VIP 0" *)
  output s_axis_tx_tready;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TDATA" *)
  input [63:0]s_axis_tx_tdata;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TKEEP" *)
  input [7:0]s_axis_tx_tkeep;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TLAST" *)
  input s_axis_tx_tlast;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TVALID" *)
  input s_axis_tx_tvalid;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 s_axis_tx TUSER" *)
  input [3:0]s_axis_tx_tuser;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control tx_cfg_gnt" *)
  (* X_INTERFACE_MODE = "slave pcie2_cfg_control" *)
  input tx_cfg_gnt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TDATA" *)
  (* X_INTERFACE_MODE = "master m_axis_rx" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME m_axis_rx, TDATA_NUM_BYTES 8, TDEST_WIDTH 0, TID_WIDTH 0, TUSER_WIDTH 22, HAS_TREADY 1, HAS_TSTRB 0, HAS_TKEEP 1, HAS_TLAST 1, FREQ_HZ 100000000, PHASE 0.0, CLK_DOMAIN , LAYERED_METADATA undef, INSERT_VIP 0" *)
  output [63:0]m_axis_rx_tdata;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TKEEP" *)
  output [7:0]m_axis_rx_tkeep;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TLAST" *)
  output m_axis_rx_tlast;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TVALID" *)
  output m_axis_rx_tvalid;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TREADY" *)
  input m_axis_rx_tready;
  (* X_INTERFACE_INFO = "xilinx.com:interface:axis:1.0 m_axis_rx TUSER" *)
  output [21:0]m_axis_rx_tuser;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control rx_np_ok" *)
  input rx_np_ok;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control rx_np_req" *)
  input rx_np_req;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc CPLD" *)
  (* X_INTERFACE_MODE = "master pcie_cfg_fc" *)
  output [11:0]fc_cpld;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc CPLH" *)
  output [7:0]fc_cplh;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc NPD" *)
  output [11:0]fc_npd;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc NPH" *)
  output [7:0]fc_nph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc PD" *)
  output [11:0]fc_pd;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc PH" *)
  output [7:0]fc_ph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_fc:1.0 pcie_cfg_fc SEL" *)
  input [2:0]fc_sel;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_DATA" *)
  (* X_INTERFACE_MODE = "slave pcie_cfg_mgmt" *)
  output [31:0]cfg_mgmt_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_WRITE_DONE" *)
  output cfg_mgmt_rd_wr_done;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status status" *)
  output [15:0]cfg_status;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status command" *)
  output [15:0]cfg_command;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dstatus" *)
  output [15:0]cfg_dstatus;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dcommand" *)
  output [15:0]cfg_dcommand;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status lstatus" *)
  output [15:0]cfg_lstatus;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status lcommand" *)
  output [15:0]cfg_lcommand;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status dcommand2" *)
  output [15:0]cfg_dcommand2;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pcie_link_state" *)
  output [2:0]cfg_pcie_link_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_pme_en" *)
  output cfg_pmcsr_pme_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_powerstate" *)
  output [1:0]cfg_pmcsr_powerstate;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status pmcsr_pme_status" *)
  output cfg_pmcsr_pme_status;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status received_func_lvl_rst" *)
  output cfg_received_func_lvl_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt WRITE_DATA" *)
  input [31:0]cfg_mgmt_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt BYTE_EN" *)
  input [3:0]cfg_mgmt_byte_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt ADDR" *)
  input [9:0]cfg_mgmt_dwaddr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt WRITE_EN" *)
  input cfg_mgmt_wr_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READ_EN" *)
  input cfg_mgmt_rd_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt READONLY" *)
  input cfg_mgmt_wr_readonly;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err ecrc" *)
  (* X_INTERFACE_MODE = "slave pcie2_cfg_err" *)
  input cfg_err_ecrc;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err ur" *)
  input cfg_err_ur;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_timeout" *)
  input cfg_err_cpl_timeout;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_unexpect" *)
  input cfg_err_cpl_unexpect;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_abort" *)
  input cfg_err_cpl_abort;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err posted" *)
  input cfg_err_posted;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cor" *)
  input cfg_err_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err atomic_egress_blocked" *)
  input cfg_err_atomic_egress_blocked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err internal_cor" *)
  input cfg_err_internal_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err malformed" *)
  input cfg_err_malformed;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err mc_blocked" *)
  input cfg_err_mc_blocked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err poisoned" *)
  input cfg_err_poisoned;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err norecovery" *)
  input cfg_err_norecovery;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err tlp_cpl_header" *)
  input [47:0]cfg_err_tlp_cpl_header;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err cpl_rdy" *)
  output cfg_err_cpl_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err locked" *)
  input cfg_err_locked;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err acs" *)
  input cfg_err_acs;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err internal_uncor" *)
  input cfg_err_internal_uncor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control trn_pending" *)
  input cfg_trn_pending;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_halt_aspm_l0s" *)
  input cfg_pm_halt_aspm_l0s;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_halt_aspm_l1" *)
  input cfg_pm_halt_aspm_l1;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_force_state_en" *)
  input cfg_pm_force_state_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_force_state" *)
  input [1:0]cfg_pm_force_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control dsn" *)
  input [63:0]cfg_dsn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt interrupt" *)
  (* X_INTERFACE_MODE = "slave pcie2_cfg_interrupt" *)
  input cfg_interrupt;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt rdy" *)
  output cfg_interrupt_rdy;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt assert" *)
  input cfg_interrupt_assert;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt write_data" *)
  input [7:0]cfg_interrupt_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt read_data" *)
  output [7:0]cfg_interrupt_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt mmenable" *)
  output [2:0]cfg_interrupt_mmenable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msienable" *)
  output cfg_interrupt_msienable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msixenable" *)
  output cfg_interrupt_msixenable;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt msixfm" *)
  output cfg_interrupt_msixfm;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt stat" *)
  input cfg_interrupt_stat;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_interrupt:1.0 pcie2_cfg_interrupt pciecap_interrupt_msgnum" *)
  input [4:0]cfg_pciecap_interrupt_msgnum;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status turnoff" *)
  output cfg_to_turnoff;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control turnoff_ok" *)
  input cfg_turnoff_ok;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status bus_number" *)
  output [7:0]cfg_bus_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status device_number" *)
  output [4:0]cfg_device_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status function_number" *)
  output [2:0]cfg_function_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_wake" *)
  input cfg_pm_wake;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control pm_send_pme_to" *)
  input cfg_pm_send_pme_to;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_bus_number" *)
  input [7:0]cfg_ds_bus_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_device_number" *)
  input [4:0]cfg_ds_device_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_control:1.0 pcie2_cfg_control ds_function_number" *)
  input [2:0]cfg_ds_function_number;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_cfg_mgmt:1.0 pcie_cfg_mgmt TYPE1_CFG_REG_ACCESS" *)
  input cfg_mgmt_wr_rw1c_as_rw;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received" *)
  (* X_INTERFACE_MODE = "master pcie2_cfg_msg_rcvd" *)
  output cfg_msg_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd data" *)
  output [15:0]cfg_msg_data;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status bridge_serr_en" *)
  output cfg_bridge_serr_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status slot_control_electromech_il_ctl_pulse" *)
  output cfg_slot_control_electromech_il_ctl_pulse;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_corr_err_en" *)
  output cfg_root_control_syserr_corr_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_non_fatal_err_en" *)
  output cfg_root_control_syserr_non_fatal_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_syserr_fatal_err_en" *)
  output cfg_root_control_syserr_fatal_err_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status root_control_pme_int_en" *)
  output cfg_root_control_pme_int_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_corr_err_reporting_en" *)
  output cfg_aer_rooterr_corr_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_non_fatal_err_reporting_en" *)
  output cfg_aer_rooterr_non_fatal_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_fatal_err_reporting_en" *)
  output cfg_aer_rooterr_fatal_err_reporting_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_corr_err_received" *)
  output cfg_aer_rooterr_corr_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_non_fatal_err_received" *)
  output cfg_aer_rooterr_non_fatal_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status aer_rooterr_fatal_err_received" *)
  output cfg_aer_rooterr_fatal_err_received;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_cor" *)
  output cfg_msg_received_err_cor;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_non_fatal" *)
  output cfg_msg_received_err_non_fatal;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd err_fatal" *)
  output cfg_msg_received_err_fatal;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received_pm_as_nak" *)
  output cfg_msg_received_pm_as_nak;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd pm_pme" *)
  output cfg_msg_received_pm_pme;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd pme_to_ack" *)
  output cfg_msg_received_pme_to_ack;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_a" *)
  output cfg_msg_received_assert_int_a;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_b" *)
  output cfg_msg_received_assert_int_b;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_c" *)
  output cfg_msg_received_assert_int_c;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd assert_int_d" *)
  output cfg_msg_received_assert_int_d;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_a" *)
  output cfg_msg_received_deassert_int_a;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_b" *)
  output cfg_msg_received_deassert_int_b;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_c" *)
  output cfg_msg_received_deassert_int_c;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd deassert_int_d" *)
  output cfg_msg_received_deassert_int_d;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_msg_rcvd:1.0 pcie2_cfg_msg_rcvd received_setslotpowerlimit" *)
  output cfg_msg_received_setslotpowerlimit;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_change" *)
  (* X_INTERFACE_MODE = "slave pcie2_pl" *)
  input [1:0]pl_directed_link_change;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_width" *)
  input [1:0]pl_directed_link_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_speed" *)
  input pl_directed_link_speed;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_link_auton" *)
  input pl_directed_link_auton;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl upstream_prefer_deemph" *)
  input pl_upstream_prefer_deemph;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl sel_lnk_rate" *)
  output pl_sel_lnk_rate;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl sel_lnk_width" *)
  output [1:0]pl_sel_lnk_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl ltssm_state" *)
  output [5:0]pl_ltssm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl lane_reversal_mode" *)
  output [1:0]pl_lane_reversal_mode;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl phy_lnk_up" *)
  output pl_phy_lnk_up;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl tx_pm_state" *)
  output [2:0]pl_tx_pm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl rx_pm_state" *)
  output [1:0]pl_rx_pm_state;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_upcfg_cap" *)
  output pl_link_upcfg_cap;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_gen2_cap" *)
  output pl_link_gen2_cap;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl link_partner_gen2_supported" *)
  output pl_link_partner_gen2_supported;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl initial_link_width" *)
  output [2:0]pl_initial_link_width;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl directed_change_done" *)
  output pl_directed_change_done;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl received_hot_rst" *)
  output pl_received_hot_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl transmit_hot_rst" *)
  input pl_transmit_hot_rst;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_pl:1.0 pcie2_pl downstream_deemph_source" *)
  input pl_downstream_deemph_source;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err err_aer_headerlog" *)
  input [127:0]cfg_err_aer_headerlog;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_interrupt_msgnum" *)
  input [4:0]cfg_aer_interrupt_msgnum;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err err_aer_headerlog_set" *)
  output cfg_err_aer_headerlog_set;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_ecrc_check_en" *)
  output cfg_aer_ecrc_check_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_err:1.0 pcie2_cfg_err aer_ecrc_gen_en" *)
  output cfg_aer_ecrc_gen_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie2_cfg_status:1.0 pcie2_cfg_status vc_tcvc_map" *)
  output [6:0]cfg_vc_tcvc_map;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.sys_clk CLK" *)
  (* X_INTERFACE_MODE = "slave CLK.sys_clk" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.sys_clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, CLK_DOMAIN , ASSOCIATED_BUSIF , ASSOCIATED_PORT , ASSOCIATED_RESET , INSERT_VIP 0" *)
  input sys_clk;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 RST.sys_rst_n RST" *)
  (* X_INTERFACE_MODE = "slave RST.sys_rst_n" *)
  (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME RST.sys_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0" *)
  input sys_rst_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_rst_n" *)
  input pipe_mmcm_rst_n;
  (* X_INTERFACE_IGNORE = "true" *)
  input pcie_drp_clk;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DEN" *)
  (* X_INTERFACE_MODE = "slave drp" *)
  input pcie_drp_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DWE" *)
  input pcie_drp_we;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DADDR" *)
  input [8:0]pcie_drp_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DI" *)
  input [15:0]pcie_drp_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DO" *)
  output [15:0]pcie_drp_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DRDY" *)
  output pcie_drp_rdy;

  // stub module has no contents

endmodule
