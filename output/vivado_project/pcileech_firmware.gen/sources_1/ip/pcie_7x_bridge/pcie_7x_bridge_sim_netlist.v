// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// Copyright 2022-2024 Advanced Micro Devices, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2024.2 (lin64) Build 5239630 Fri Nov 08 22:34:34 MST 2024
// Date        : Fri Jul 18 01:31:37 2025
// Host        : muttti-System-Product-Name running 64-bit Ubuntu 24.04.2 LTS
// Command     : write_verilog -force -mode funcsim
//               /home/muttti/123/output/vivado_project/pcileech_firmware.gen/sources_1/ip/pcie_7x_bridge/pcie_7x_bridge_sim_netlist.v
// Design      : pcie_7x_bridge
// Purpose     : This verilog netlist is a functional simulation representation of the design and should not be modified
//               or synthesized. This netlist cannot be used for SDF annotated simulation.
// Device      : xc7a75tfgg484-2
// --------------------------------------------------------------------------------
`timescale 1 ps / 1 ps

(* CHECK_LICENSE_TYPE = "pcie_7x_bridge,pcie_7x_bridge_pcie2_top,{}" *) (* DowngradeIPIdentifiedWarnings = "yes" *) (* X_CORE_INFO = "pcie_7x_bridge_pcie2_top,Vivado 2024.2" *) 
(* NotValidForBitStream *)
module pcie_7x_bridge
   (pci_exp_txp,
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
    pcie_drp_rdy);
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txp" *) (* X_INTERFACE_MODE = "master" *) output [0:0]pci_exp_txp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt txn" *) output [0:0]pci_exp_txn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxp" *) input [0:0]pci_exp_rxp;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pcie_7x_mgt:1.0 pcie_7x_mgt rxn" *) input [0:0]pci_exp_rxn;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_in" *) (* X_INTERFACE_MODE = "slave" *) input pipe_pclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxusrclk_in" *) input pipe_rxusrclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_in" *) input [0:0]pipe_rxoutclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock dclk_in" *) input pipe_dclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk1_in" *) input pipe_userclk1_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock userclk2_in" *) input pipe_userclk2_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock oobclk_in" *) input pipe_oobclk_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_lock_in" *) input pipe_mmcm_lock_in;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock txoutclk_out" *) output pipe_txoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock rxoutclk_out" *) output [0:0]pipe_rxoutclk_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock pclk_sel_out" *) output [0:0]pipe_pclk_sel_out;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock gen3_out" *) output pipe_gen3_out;
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.user_clk_out CLK" *) (* X_INTERFACE_MODE = "master" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.user_clk_out, ASSOCIATED_BUSIF m_axis_rx:s_axis_tx, FREQ_HZ 125000000, ASSOCIATED_RESET user_reset_out, FREQ_TOLERANCE_HZ 0, PHASE 0.0, INSERT_VIP 0" *) output user_clk_out;
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
  (* X_INTERFACE_INFO = "xilinx.com:signal:clock:1.0 CLK.sys_clk CLK" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME CLK.sys_clk, FREQ_HZ 100000000, FREQ_TOLERANCE_HZ 0, PHASE 0.0, INSERT_VIP 0" *) input sys_clk;
  (* X_INTERFACE_INFO = "xilinx.com:signal:reset:1.0 RST.sys_rst_n RST" *) (* X_INTERFACE_MODE = "slave" *) (* X_INTERFACE_PARAMETER = "XIL_INTERFACENAME RST.sys_rst_n, POLARITY ACTIVE_LOW, INSERT_VIP 0" *) input sys_rst_n;
  (* X_INTERFACE_INFO = "xilinx.com:interface:pipe_clock:1.0 pipe_clock mmcm_rst_n" *) input pipe_mmcm_rst_n;
  input pcie_drp_clk;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DEN" *) (* X_INTERFACE_MODE = "slave" *) input pcie_drp_en;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DWE" *) input pcie_drp_we;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DADDR" *) input [8:0]pcie_drp_addr;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DI" *) input [15:0]pcie_drp_di;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DO" *) output [15:0]pcie_drp_do;
  (* X_INTERFACE_INFO = "xilinx.com:interface:drp:1.0 drp DRDY" *) output pcie_drp_rdy;

  wire \<const0> ;
  wire \<const1> ;
  wire cfg_aer_ecrc_check_en;
  wire cfg_aer_ecrc_gen_en;
  wire [4:0]cfg_aer_interrupt_msgnum;
  wire cfg_aer_rooterr_corr_err_received;
  wire cfg_aer_rooterr_corr_err_reporting_en;
  wire cfg_aer_rooterr_fatal_err_received;
  wire cfg_aer_rooterr_fatal_err_reporting_en;
  wire cfg_aer_rooterr_non_fatal_err_received;
  wire cfg_aer_rooterr_non_fatal_err_reporting_en;
  wire cfg_bridge_serr_en;
  wire [7:0]cfg_bus_number;
  wire [10:0]\^cfg_command ;
  wire [14:0]\^cfg_dcommand ;
  wire [11:0]\^cfg_dcommand2 ;
  wire [4:0]cfg_device_number;
  wire [7:0]cfg_ds_bus_number;
  wire [4:0]cfg_ds_device_number;
  wire [2:0]cfg_ds_function_number;
  wire [63:0]cfg_dsn;
  wire [5:0]\^cfg_dstatus ;
  wire [127:0]cfg_err_aer_headerlog;
  wire cfg_err_aer_headerlog_set;
  wire cfg_err_atomic_egress_blocked;
  wire cfg_err_cor;
  wire cfg_err_cpl_abort;
  wire cfg_err_cpl_rdy;
  wire cfg_err_cpl_timeout;
  wire cfg_err_cpl_unexpect;
  wire cfg_err_ecrc;
  wire cfg_err_internal_cor;
  wire cfg_err_internal_uncor;
  wire cfg_err_locked;
  wire cfg_err_malformed;
  wire cfg_err_mc_blocked;
  wire cfg_err_norecovery;
  wire cfg_err_poisoned;
  wire cfg_err_posted;
  wire [47:0]cfg_err_tlp_cpl_header;
  wire cfg_err_ur;
  wire [2:0]cfg_function_number;
  wire cfg_interrupt;
  wire cfg_interrupt_assert;
  wire [7:0]cfg_interrupt_di;
  wire [7:0]cfg_interrupt_do;
  wire [2:0]cfg_interrupt_mmenable;
  wire cfg_interrupt_msienable;
  wire cfg_interrupt_msixenable;
  wire cfg_interrupt_msixfm;
  wire cfg_interrupt_rdy;
  wire cfg_interrupt_stat;
  wire [11:0]\^cfg_lcommand ;
  wire [15:0]\^cfg_lstatus ;
  wire [3:0]cfg_mgmt_byte_en;
  wire [31:0]cfg_mgmt_di;
  wire [31:0]cfg_mgmt_do;
  wire [9:0]cfg_mgmt_dwaddr;
  wire cfg_mgmt_rd_en;
  wire cfg_mgmt_rd_wr_done;
  wire cfg_mgmt_wr_en;
  wire cfg_mgmt_wr_readonly;
  wire cfg_mgmt_wr_rw1c_as_rw;
  wire [15:0]cfg_msg_data;
  wire cfg_msg_received;
  wire cfg_msg_received_assert_int_a;
  wire cfg_msg_received_assert_int_b;
  wire cfg_msg_received_assert_int_c;
  wire cfg_msg_received_assert_int_d;
  wire cfg_msg_received_deassert_int_a;
  wire cfg_msg_received_deassert_int_b;
  wire cfg_msg_received_deassert_int_c;
  wire cfg_msg_received_deassert_int_d;
  wire cfg_msg_received_err_cor;
  wire cfg_msg_received_err_fatal;
  wire cfg_msg_received_err_non_fatal;
  wire cfg_msg_received_pm_as_nak;
  wire cfg_msg_received_pm_pme;
  wire cfg_msg_received_pme_to_ack;
  wire cfg_msg_received_setslotpowerlimit;
  wire [2:0]cfg_pcie_link_state;
  wire [4:0]cfg_pciecap_interrupt_msgnum;
  wire [1:0]cfg_pm_force_state;
  wire cfg_pm_force_state_en;
  wire cfg_pm_halt_aspm_l0s;
  wire cfg_pm_halt_aspm_l1;
  wire cfg_pm_wake;
  wire cfg_pmcsr_pme_en;
  wire cfg_pmcsr_pme_status;
  wire [1:0]cfg_pmcsr_powerstate;
  wire cfg_received_func_lvl_rst;
  wire cfg_root_control_pme_int_en;
  wire cfg_root_control_syserr_corr_err_en;
  wire cfg_root_control_syserr_fatal_err_en;
  wire cfg_root_control_syserr_non_fatal_err_en;
  wire cfg_slot_control_electromech_il_ctl_pulse;
  wire cfg_to_turnoff;
  wire cfg_trn_pending;
  wire cfg_turnoff_ok;
  wire [6:0]cfg_vc_tcvc_map;
  wire [11:0]fc_cpld;
  wire [7:0]fc_cplh;
  wire [11:0]fc_npd;
  wire [7:0]fc_nph;
  wire [11:0]fc_pd;
  wire [7:0]fc_ph;
  wire [2:0]fc_sel;
  wire [63:0]m_axis_rx_tdata;
  wire [7:4]\^m_axis_rx_tkeep ;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [21:0]\^m_axis_rx_tuser ;
  wire m_axis_rx_tvalid;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire [8:0]pcie_drp_addr;
  wire pcie_drp_clk;
  wire [15:0]pcie_drp_di;
  wire [15:0]pcie_drp_do;
  wire pcie_drp_en;
  wire pcie_drp_rdy;
  wire pcie_drp_we;
  wire pipe_dclk_in;
  wire pipe_mmcm_lock_in;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire pipe_txoutclk_out;
  wire pipe_userclk1_in;
  wire pipe_userclk2_in;
  wire pl_directed_change_done;
  wire pl_directed_link_auton;
  wire [1:0]pl_directed_link_change;
  wire pl_directed_link_speed;
  wire [1:0]pl_directed_link_width;
  wire pl_downstream_deemph_source;
  wire [2:0]pl_initial_link_width;
  wire [1:0]pl_lane_reversal_mode;
  wire pl_link_gen2_cap;
  wire pl_link_partner_gen2_supported;
  wire pl_link_upcfg_cap;
  wire [5:0]pl_ltssm_state;
  wire pl_phy_lnk_up;
  wire pl_received_hot_rst;
  wire [1:0]pl_rx_pm_state;
  wire pl_sel_lnk_rate;
  wire [1:0]pl_sel_lnk_width;
  wire pl_transmit_hot_rst;
  wire [2:0]pl_tx_pm_state;
  wire pl_upstream_prefer_deemph;
  wire rx_np_ok;
  wire rx_np_req;
  wire [63:0]s_axis_tx_tdata;
  wire [7:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire s_axis_tx_tready;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire sys_clk;
  wire sys_rst_n;
  wire [5:0]tx_buf_av;
  wire tx_cfg_gnt;
  wire tx_cfg_req;
  wire tx_err_drop;
  wire user_clk_out;
  wire user_lnk_up;
  wire user_reset_out;
  wire NLW_inst_ext_ch_gt_drpclk_UNCONNECTED;
  wire NLW_inst_int_dclk_out_UNCONNECTED;
  wire NLW_inst_int_mmcm_lock_out_UNCONNECTED;
  wire NLW_inst_int_oobclk_out_UNCONNECTED;
  wire NLW_inst_int_pclk_out_slave_UNCONNECTED;
  wire NLW_inst_int_pipe_rxusrclk_out_UNCONNECTED;
  wire NLW_inst_int_userclk1_out_UNCONNECTED;
  wire NLW_inst_int_userclk2_out_UNCONNECTED;
  wire NLW_inst_pipe_gen3_out_UNCONNECTED;
  wire NLW_inst_pipe_qrst_idle_UNCONNECTED;
  wire NLW_inst_pipe_rate_idle_UNCONNECTED;
  wire NLW_inst_pipe_rst_idle_UNCONNECTED;
  wire NLW_inst_qpll_drp_clk_UNCONNECTED;
  wire NLW_inst_qpll_drp_gen3_UNCONNECTED;
  wire NLW_inst_qpll_drp_ovrd_UNCONNECTED;
  wire NLW_inst_qpll_drp_rst_n_UNCONNECTED;
  wire NLW_inst_qpll_drp_start_UNCONNECTED;
  wire NLW_inst_qpll_qplld_UNCONNECTED;
  wire NLW_inst_startup_cfgclk_UNCONNECTED;
  wire NLW_inst_startup_cfgmclk_UNCONNECTED;
  wire NLW_inst_startup_eos_UNCONNECTED;
  wire NLW_inst_startup_preq_UNCONNECTED;
  wire NLW_inst_user_app_rdy_UNCONNECTED;
  wire [15:3]NLW_inst_cfg_command_UNCONNECTED;
  wire [15:15]NLW_inst_cfg_dcommand_UNCONNECTED;
  wire [15:12]NLW_inst_cfg_dcommand2_UNCONNECTED;
  wire [15:4]NLW_inst_cfg_dstatus_UNCONNECTED;
  wire [15:2]NLW_inst_cfg_lcommand_UNCONNECTED;
  wire [12:2]NLW_inst_cfg_lstatus_UNCONNECTED;
  wire [15:0]NLW_inst_cfg_status_UNCONNECTED;
  wire [11:0]NLW_inst_common_commands_out_UNCONNECTED;
  wire [15:0]NLW_inst_ext_ch_gt_drpdo_UNCONNECTED;
  wire [0:0]NLW_inst_ext_ch_gt_drprdy_UNCONNECTED;
  wire [0:0]NLW_inst_gt_ch_drp_rdy_UNCONNECTED;
  wire [31:0]NLW_inst_icap_o_UNCONNECTED;
  wire [1:0]NLW_inst_int_qplllock_out_UNCONNECTED;
  wire [1:0]NLW_inst_int_qplloutclk_out_UNCONNECTED;
  wire [1:0]NLW_inst_int_qplloutrefclk_out_UNCONNECTED;
  wire [0:0]NLW_inst_int_rxoutclk_out_UNCONNECTED;
  wire [3:0]NLW_inst_m_axis_rx_tkeep_UNCONNECTED;
  wire [20:9]NLW_inst_m_axis_rx_tuser_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_cpll_lock_UNCONNECTED;
  wire [31:0]NLW_inst_pipe_debug_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_0_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_1_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_2_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_3_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_4_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_5_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_6_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_7_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_8_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_debug_9_UNCONNECTED;
  wire [14:0]NLW_inst_pipe_dmonitorout_UNCONNECTED;
  wire [6:0]NLW_inst_pipe_drp_fsm_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_eyescandataerror_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_qpll_lock_UNCONNECTED;
  wire [11:0]NLW_inst_pipe_qrst_fsm_UNCONNECTED;
  wire [4:0]NLW_inst_pipe_rate_fsm_UNCONNECTED;
  wire [4:0]NLW_inst_pipe_rst_fsm_UNCONNECTED;
  wire [2:0]NLW_inst_pipe_rxbufstatus_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxcommadet_UNCONNECTED;
  wire [7:0]NLW_inst_pipe_rxdisperr_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxdlysresetdone_UNCONNECTED;
  wire [7:0]NLW_inst_pipe_rxnotintable_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxphaligndone_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxpmaresetdone_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxprbserr_UNCONNECTED;
  wire [2:0]NLW_inst_pipe_rxstatus_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_rxsyncdone_UNCONNECTED;
  wire [6:0]NLW_inst_pipe_sync_fsm_rx_UNCONNECTED;
  wire [5:0]NLW_inst_pipe_sync_fsm_tx_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_0_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_1_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_2_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_3_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_4_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_5_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_6_sigs_UNCONNECTED;
  wire [24:0]NLW_inst_pipe_tx_7_sigs_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_txdlysresetdone_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_txphaligndone_UNCONNECTED;
  wire [0:0]NLW_inst_pipe_txphinitdone_UNCONNECTED;
  wire [1:0]NLW_inst_qpll_qpllreset_UNCONNECTED;

  assign cfg_command[15] = \<const0> ;
  assign cfg_command[14] = \<const0> ;
  assign cfg_command[13] = \<const0> ;
  assign cfg_command[12] = \<const0> ;
  assign cfg_command[11] = \<const0> ;
  assign cfg_command[10] = \^cfg_command [10];
  assign cfg_command[9] = \<const0> ;
  assign cfg_command[8] = \^cfg_command [8];
  assign cfg_command[7] = \<const0> ;
  assign cfg_command[6] = \<const0> ;
  assign cfg_command[5] = \<const0> ;
  assign cfg_command[4] = \<const0> ;
  assign cfg_command[3] = \<const0> ;
  assign cfg_command[2:0] = \^cfg_command [2:0];
  assign cfg_dcommand[15] = \<const0> ;
  assign cfg_dcommand[14:0] = \^cfg_dcommand [14:0];
  assign cfg_dcommand2[15] = \<const0> ;
  assign cfg_dcommand2[14] = \<const0> ;
  assign cfg_dcommand2[13] = \<const0> ;
  assign cfg_dcommand2[12] = \<const0> ;
  assign cfg_dcommand2[11:0] = \^cfg_dcommand2 [11:0];
  assign cfg_dstatus[15] = \<const0> ;
  assign cfg_dstatus[14] = \<const0> ;
  assign cfg_dstatus[13] = \<const0> ;
  assign cfg_dstatus[12] = \<const0> ;
  assign cfg_dstatus[11] = \<const0> ;
  assign cfg_dstatus[10] = \<const0> ;
  assign cfg_dstatus[9] = \<const0> ;
  assign cfg_dstatus[8] = \<const0> ;
  assign cfg_dstatus[7] = \<const0> ;
  assign cfg_dstatus[6] = \<const0> ;
  assign cfg_dstatus[5] = \^cfg_dstatus [5];
  assign cfg_dstatus[4] = \<const0> ;
  assign cfg_dstatus[3:0] = \^cfg_dstatus [3:0];
  assign cfg_lcommand[15] = \<const0> ;
  assign cfg_lcommand[14] = \<const0> ;
  assign cfg_lcommand[13] = \<const0> ;
  assign cfg_lcommand[12] = \<const0> ;
  assign cfg_lcommand[11:3] = \^cfg_lcommand [11:3];
  assign cfg_lcommand[2] = \<const0> ;
  assign cfg_lcommand[1:0] = \^cfg_lcommand [1:0];
  assign cfg_lstatus[15:13] = \^cfg_lstatus [15:13];
  assign cfg_lstatus[12] = \<const1> ;
  assign cfg_lstatus[11] = \^cfg_lstatus [11];
  assign cfg_lstatus[10] = \<const0> ;
  assign cfg_lstatus[9] = \<const0> ;
  assign cfg_lstatus[8] = \<const0> ;
  assign cfg_lstatus[7:4] = \^cfg_lstatus [7:4];
  assign cfg_lstatus[3] = \<const0> ;
  assign cfg_lstatus[2] = \<const0> ;
  assign cfg_lstatus[1:0] = \^cfg_lstatus [1:0];
  assign cfg_status[15] = \<const0> ;
  assign cfg_status[14] = \<const0> ;
  assign cfg_status[13] = \<const0> ;
  assign cfg_status[12] = \<const0> ;
  assign cfg_status[11] = \<const0> ;
  assign cfg_status[10] = \<const0> ;
  assign cfg_status[9] = \<const0> ;
  assign cfg_status[8] = \<const0> ;
  assign cfg_status[7] = \<const0> ;
  assign cfg_status[6] = \<const0> ;
  assign cfg_status[5] = \<const0> ;
  assign cfg_status[4] = \<const0> ;
  assign cfg_status[3] = \<const0> ;
  assign cfg_status[2] = \<const0> ;
  assign cfg_status[1] = \<const0> ;
  assign cfg_status[0] = \<const0> ;
  assign m_axis_rx_tkeep[7:4] = \^m_axis_rx_tkeep [7:4];
  assign m_axis_rx_tkeep[3] = \<const1> ;
  assign m_axis_rx_tkeep[2] = \<const1> ;
  assign m_axis_rx_tkeep[1] = \<const1> ;
  assign m_axis_rx_tkeep[0] = \<const1> ;
  assign m_axis_rx_tuser[21] = \^m_axis_rx_tuser [21];
  assign m_axis_rx_tuser[20] = \<const0> ;
  assign m_axis_rx_tuser[19:17] = \^m_axis_rx_tuser [19:17];
  assign m_axis_rx_tuser[16] = \<const0> ;
  assign m_axis_rx_tuser[15] = \<const0> ;
  assign m_axis_rx_tuser[14] = \^m_axis_rx_tuser [14];
  assign m_axis_rx_tuser[13] = \<const0> ;
  assign m_axis_rx_tuser[12] = \<const0> ;
  assign m_axis_rx_tuser[11] = \<const0> ;
  assign m_axis_rx_tuser[10] = \<const0> ;
  assign m_axis_rx_tuser[9] = \<const0> ;
  assign m_axis_rx_tuser[8:0] = \^m_axis_rx_tuser [8:0];
  assign pipe_gen3_out = \<const0> ;
  assign user_app_rdy = \<const1> ;
  GND GND
       (.G(\<const0> ));
  VCC VCC
       (.P(\<const1> ));
  (* CFG_CTL_IF = "TRUE" *) 
  (* CFG_FC_IF = "TRUE" *) 
  (* CFG_MGMT_IF = "TRUE" *) 
  (* CFG_STATUS_IF = "TRUE" *) 
  (* CLASS_CODE = "020000" *) 
  (* C_DATA_WIDTH = "64" *) 
  (* DowngradeIPIdentifiedWarnings = "yes" *) 
  (* ENABLE_JTAG_DBG = "FALSE" *) 
  (* ERR_REPORTING_IF = "TRUE" *) 
  (* EXT_CH_GT_DRP = "FALSE" *) 
  (* EXT_PIPE_INTERFACE = "FALSE" *) 
  (* EXT_STARTUP_PRIMITIVE = "FALSE" *) 
  (* KEEP_WIDTH = "8" *) 
  (* LINK_CAP_MAX_LINK_WIDTH = "1" *) 
  (* PCIE_ASYNC_EN = "FALSE" *) 
  (* PCIE_EXT_CLK = "TRUE" *) 
  (* PCIE_EXT_GT_COMMON = "FALSE" *) 
  (* PCIE_ID_IF = "FALSE" *) 
  (* PIPE_SIM = "FALSE" *) 
  (* PL_INTERFACE = "TRUE" *) 
  (* RCV_MSG_IF = "TRUE" *) 
  (* REDUCE_OOB_FREQ = "FALSE" *) 
  (* SHARED_LOGIC_IN_CORE = "FALSE" *) 
  (* TRANSCEIVER_CTRL_STATUS_PORTS = "FALSE" *) 
  (* bar_0 = "FFFFFC04" *) 
  (* bar_1 = "FFFFFFFF" *) 
  (* bar_2 = "00000000" *) 
  (* bar_3 = "00000000" *) 
  (* bar_4 = "00000000" *) 
  (* bar_5 = "00000000" *) 
  (* bram_lat = "0" *) 
  (* c_aer_base_ptr = "000" *) 
  (* c_aer_cap_ecrc_check_capable = "FALSE" *) 
  (* c_aer_cap_ecrc_gen_capable = "FALSE" *) 
  (* c_aer_cap_multiheader = "FALSE" *) 
  (* c_aer_cap_nextptr = "000" *) 
  (* c_aer_cap_on = "FALSE" *) 
  (* c_aer_cap_optional_err_support = "000000" *) 
  (* c_aer_cap_permit_rooterr_update = "FALSE" *) 
  (* c_buf_opt_bma = "TRUE" *) 
  (* c_component_name = "pcie_7x_bridge" *) 
  (* c_cpl_inf = "TRUE" *) 
  (* c_cpl_infinite = "TRUE" *) 
  (* c_cpl_timeout_disable_sup = "FALSE" *) 
  (* c_cpl_timeout_range = "0010" *) 
  (* c_cpl_timeout_ranges_sup = "2" *) 
  (* c_d1_support = "FALSE" *) 
  (* c_d2_support = "FALSE" *) 
  (* c_de_emph = "FALSE" *) 
  (* c_dev_cap2_ari_forwarding_supported = "FALSE" *) 
  (* c_dev_cap2_atomicop32_completer_supported = "FALSE" *) 
  (* c_dev_cap2_atomicop64_completer_supported = "FALSE" *) 
  (* c_dev_cap2_atomicop_routing_supported = "FALSE" *) 
  (* c_dev_cap2_cas128_completer_supported = "FALSE" *) 
  (* c_dev_cap2_tph_completer_supported = "00" *) 
  (* c_dev_control_ext_tag_default = "FALSE" *) 
  (* c_dev_port_type = "0" *) 
  (* c_dis_lane_reverse = "TRUE" *) 
  (* c_disable_rx_poisoned_resp = "FALSE" *) 
  (* c_disable_scrambling = "FALSE" *) 
  (* c_disable_tx_aspm_l0s = "FALSE" *) 
  (* c_dll_lnk_actv_cap = "FALSE" *) 
  (* c_dsi_bool = "FALSE" *) 
  (* c_dsn_base_ptr = "100" *) 
  (* c_dsn_cap_enabled = "TRUE" *) 
  (* c_dsn_next_ptr = "000" *) 
  (* c_enable_msg_route = "00000000000" *) 
  (* c_ep_l0s_accpt_lat = "0" *) 
  (* c_ep_l1_accpt_lat = "7" *) 
  (* c_ext_pci_cfg_space_addr = "3FF" *) 
  (* c_external_clocking = "TRUE" *) 
  (* c_fc_cpld = "461" *) 
  (* c_fc_cplh = "36" *) 
  (* c_fc_npd = "24" *) 
  (* c_fc_nph = "12" *) 
  (* c_fc_pd = "437" *) 
  (* c_fc_ph = "32" *) 
  (* c_gen1 = "1'b0" *) 
  (* c_header_type = "00" *) 
  (* c_hw_auton_spd_disable = "FALSE" *) 
  (* c_int_width = "64" *) 
  (* c_last_cfg_dw = "10C" *) 
  (* c_link_cap_aspm_optionality = "FALSE" *) 
  (* c_ll_ack_timeout = "0000" *) 
  (* c_ll_ack_timeout_enable = "FALSE" *) 
  (* c_ll_ack_timeout_function = "0" *) 
  (* c_ll_replay_timeout = "0000" *) 
  (* c_ll_replay_timeout_enable = "FALSE" *) 
  (* c_ll_replay_timeout_func = "1" *) 
  (* c_lnk_bndwdt_notif = "FALSE" *) 
  (* c_msi = "0" *) 
  (* c_msi_64b_addr = "TRUE" *) 
  (* c_msi_cap_on = "TRUE" *) 
  (* c_msi_mult_msg_extn = "0" *) 
  (* c_msi_per_vctr_mask_cap = "FALSE" *) 
  (* c_msix_cap_on = "TRUE" *) 
  (* c_msix_next_ptr = "00" *) 
  (* c_msix_pba_bir = "0" *) 
  (* c_msix_pba_offset = "0" *) 
  (* c_msix_table_bir = "0" *) 
  (* c_msix_table_offset = "0" *) 
  (* c_msix_table_size = "000" *) 
  (* c_pci_cfg_space_addr = "3F" *) 
  (* c_pcie_blk_locn = "0" *) 
  (* c_pcie_cap_next_ptr = "9C" *) 
  (* c_pcie_cap_slot_implemented = "FALSE" *) 
  (* c_pcie_dbg_ports = "TRUE" *) 
  (* c_pcie_fast_config = "0" *) 
  (* c_perf_level_high = "TRUE" *) 
  (* c_phantom_functions = "0" *) 
  (* c_pm_cap_next_ptr = "48" *) 
  (* c_pme_support = "0F" *) 
  (* c_rbar_base_ptr = "000" *) 
  (* c_rbar_cap_control_encodedbar0 = "00" *) 
  (* c_rbar_cap_control_encodedbar1 = "00" *) 
  (* c_rbar_cap_control_encodedbar2 = "00" *) 
  (* c_rbar_cap_control_encodedbar3 = "00" *) 
  (* c_rbar_cap_control_encodedbar4 = "00" *) 
  (* c_rbar_cap_control_encodedbar5 = "00" *) 
  (* c_rbar_cap_index0 = "0" *) 
  (* c_rbar_cap_index1 = "0" *) 
  (* c_rbar_cap_index2 = "0" *) 
  (* c_rbar_cap_index3 = "0" *) 
  (* c_rbar_cap_index4 = "0" *) 
  (* c_rbar_cap_index5 = "0" *) 
  (* c_rbar_cap_nextptr = "000" *) 
  (* c_rbar_cap_on = "FALSE" *) 
  (* c_rbar_cap_sup0 = "00001" *) 
  (* c_rbar_cap_sup1 = "00001" *) 
  (* c_rbar_cap_sup2 = "00001" *) 
  (* c_rbar_cap_sup3 = "00001" *) 
  (* c_rbar_cap_sup4 = "00001" *) 
  (* c_rbar_cap_sup5 = "00001" *) 
  (* c_rbar_num = "0" *) 
  (* c_rcb = "0" *) 
  (* c_recrc_check = "0" *) 
  (* c_recrc_check_trim = "FALSE" *) 
  (* c_rev_gt_order = "FALSE" *) 
  (* c_root_cap_crs = "FALSE" *) 
  (* c_rx_raddr_lat = "0" *) 
  (* c_rx_ram_limit = "7FF" *) 
  (* c_rx_rdata_lat = "2" *) 
  (* c_rx_write_lat = "0" *) 
  (* c_silicon_rev = "2" *) 
  (* c_slot_cap_attn_butn = "FALSE" *) 
  (* c_slot_cap_attn_ind = "FALSE" *) 
  (* c_slot_cap_elec_interlock = "FALSE" *) 
  (* c_slot_cap_hotplug_cap = "FALSE" *) 
  (* c_slot_cap_hotplug_surprise = "FALSE" *) 
  (* c_slot_cap_mrl = "FALSE" *) 
  (* c_slot_cap_no_cmd_comp_sup = "FALSE" *) 
  (* c_slot_cap_physical_slot_num = "0" *) 
  (* c_slot_cap_pwr_ctrl = "FALSE" *) 
  (* c_slot_cap_pwr_ind = "FALSE" *) 
  (* c_slot_cap_pwr_limit_scale = "0" *) 
  (* c_slot_cap_pwr_limit_value = "0" *) 
  (* c_surprise_dn_err_cap = "FALSE" *) 
  (* c_trgt_lnk_spd = "0" *) 
  (* c_trn_np_fc = "TRUE" *) 
  (* c_tx_last_tlp = "29" *) 
  (* c_tx_raddr_lat = "0" *) 
  (* c_tx_rdata_lat = "2" *) 
  (* c_tx_write_lat = "0" *) 
  (* c_upconfig_capable = "TRUE" *) 
  (* c_upstream_facing = "TRUE" *) 
  (* c_ur_atomic = "FALSE" *) 
  (* c_ur_inv_req = "TRUE" *) 
  (* c_ur_prs_response = "TRUE" *) 
  (* c_vc_base_ptr = "000" *) 
  (* c_vc_cap_enabled = "FALSE" *) 
  (* c_vc_cap_reject_snoop = "FALSE" *) 
  (* c_vc_next_ptr = "000" *) 
  (* c_vsec_base_ptr = "000" *) 
  (* c_vsec_cap_enabled = "FALSE" *) 
  (* c_vsec_next_ptr = "000" *) 
  (* c_xlnx_ref_board = "NONE" *) 
  (* cap_ver = "2" *) 
  (* cardbus_cis_ptr = "00000000" *) 
  (* cmps = "2" *) 
  (* con_scl_fctr_d0_state = "0" *) 
  (* con_scl_fctr_d1_state = "0" *) 
  (* con_scl_fctr_d2_state = "0" *) 
  (* con_scl_fctr_d3_state = "0" *) 
  (* cost_table = "1" *) 
  (* d1_sup = "0" *) 
  (* d2_sup = "0" *) 
  (* dev_id = "8125" *) 
  (* dev_port_type = "0000" *) 
  (* dis_scl_fctr_d0_state = "0" *) 
  (* dis_scl_fctr_d1_state = "0" *) 
  (* dis_scl_fctr_d2_state = "0" *) 
  (* dis_scl_fctr_d3_state = "0" *) 
  (* dsi = "0" *) 
  (* ep_l0s_accpt_lat = "000" *) 
  (* ep_l1_accpt_lat = "111" *) 
  (* ext_tag_fld_sup = "FALSE" *) 
  (* int_pin = "1" *) 
  (* intx = "TRUE" *) 
  (* max_lnk_spd = "1" *) 
  (* max_lnk_wdt = "000001" *) 
  (* mps = "010" *) 
  (* no_soft_rst = "TRUE" *) 
  (* pci_exp_int_freq = "1" *) 
  (* pci_exp_ref_freq = "0" *) 
  (* phantm_func_sup = "00" *) 
  (* pme_sup = "0F" *) 
  (* pwr_con_d0_state = "00" *) 
  (* pwr_con_d1_state = "00" *) 
  (* pwr_con_d2_state = "00" *) 
  (* pwr_con_d3_state = "00" *) 
  (* pwr_dis_d0_state = "00" *) 
  (* pwr_dis_d1_state = "00" *) 
  (* pwr_dis_d2_state = "00" *) 
  (* pwr_dis_d3_state = "00" *) 
  (* rev_id = "04" *) 
  (* slot_clk = "TRUE" *) 
  (* subsys_id = "7" *) 
  (* subsys_ven_id = "4332" *) 
  (* ven_id = "10ec" *) 
  (* xrom_bar = "00000000" *) 
  pcie_7x_bridge_pcie2_top inst
       (.cfg_aer_ecrc_check_en(cfg_aer_ecrc_check_en),
        .cfg_aer_ecrc_gen_en(cfg_aer_ecrc_gen_en),
        .cfg_aer_interrupt_msgnum(cfg_aer_interrupt_msgnum),
        .cfg_aer_rooterr_corr_err_received(cfg_aer_rooterr_corr_err_received),
        .cfg_aer_rooterr_corr_err_reporting_en(cfg_aer_rooterr_corr_err_reporting_en),
        .cfg_aer_rooterr_fatal_err_received(cfg_aer_rooterr_fatal_err_received),
        .cfg_aer_rooterr_fatal_err_reporting_en(cfg_aer_rooterr_fatal_err_reporting_en),
        .cfg_aer_rooterr_non_fatal_err_received(cfg_aer_rooterr_non_fatal_err_received),
        .cfg_aer_rooterr_non_fatal_err_reporting_en(cfg_aer_rooterr_non_fatal_err_reporting_en),
        .cfg_bridge_serr_en(cfg_bridge_serr_en),
        .cfg_bus_number(cfg_bus_number),
        .cfg_command({NLW_inst_cfg_command_UNCONNECTED[15:11],\^cfg_command }),
        .cfg_dcommand({NLW_inst_cfg_dcommand_UNCONNECTED[15],\^cfg_dcommand }),
        .cfg_dcommand2({NLW_inst_cfg_dcommand2_UNCONNECTED[15:12],\^cfg_dcommand2 }),
        .cfg_dev_id_pf0({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1}),
        .cfg_device_number(cfg_device_number),
        .cfg_ds_bus_number(cfg_ds_bus_number),
        .cfg_ds_device_number(cfg_ds_device_number),
        .cfg_ds_function_number(cfg_ds_function_number),
        .cfg_dsn(cfg_dsn),
        .cfg_dstatus({NLW_inst_cfg_dstatus_UNCONNECTED[15:6],\^cfg_dstatus }),
        .cfg_err_acs(1'b0),
        .cfg_err_aer_headerlog(cfg_err_aer_headerlog),
        .cfg_err_aer_headerlog_set(cfg_err_aer_headerlog_set),
        .cfg_err_atomic_egress_blocked(cfg_err_atomic_egress_blocked),
        .cfg_err_cor(cfg_err_cor),
        .cfg_err_cpl_abort(cfg_err_cpl_abort),
        .cfg_err_cpl_rdy(cfg_err_cpl_rdy),
        .cfg_err_cpl_timeout(cfg_err_cpl_timeout),
        .cfg_err_cpl_unexpect(cfg_err_cpl_unexpect),
        .cfg_err_ecrc(cfg_err_ecrc),
        .cfg_err_internal_cor(cfg_err_internal_cor),
        .cfg_err_internal_uncor(cfg_err_internal_uncor),
        .cfg_err_locked(cfg_err_locked),
        .cfg_err_malformed(cfg_err_malformed),
        .cfg_err_mc_blocked(cfg_err_mc_blocked),
        .cfg_err_norecovery(cfg_err_norecovery),
        .cfg_err_poisoned(cfg_err_poisoned),
        .cfg_err_posted(cfg_err_posted),
        .cfg_err_tlp_cpl_header(cfg_err_tlp_cpl_header),
        .cfg_err_ur(cfg_err_ur),
        .cfg_function_number(cfg_function_number),
        .cfg_interrupt(cfg_interrupt),
        .cfg_interrupt_assert(cfg_interrupt_assert),
        .cfg_interrupt_di(cfg_interrupt_di),
        .cfg_interrupt_do(cfg_interrupt_do),
        .cfg_interrupt_mmenable(cfg_interrupt_mmenable),
        .cfg_interrupt_msienable(cfg_interrupt_msienable),
        .cfg_interrupt_msixenable(cfg_interrupt_msixenable),
        .cfg_interrupt_msixfm(cfg_interrupt_msixfm),
        .cfg_interrupt_rdy(cfg_interrupt_rdy),
        .cfg_interrupt_stat(cfg_interrupt_stat),
        .cfg_lcommand({NLW_inst_cfg_lcommand_UNCONNECTED[15:12],\^cfg_lcommand }),
        .cfg_lstatus(\^cfg_lstatus ),
        .cfg_mgmt_byte_en(cfg_mgmt_byte_en),
        .cfg_mgmt_di(cfg_mgmt_di),
        .cfg_mgmt_do(cfg_mgmt_do),
        .cfg_mgmt_dwaddr(cfg_mgmt_dwaddr),
        .cfg_mgmt_rd_en(cfg_mgmt_rd_en),
        .cfg_mgmt_rd_wr_done(cfg_mgmt_rd_wr_done),
        .cfg_mgmt_wr_en(cfg_mgmt_wr_en),
        .cfg_mgmt_wr_readonly(cfg_mgmt_wr_readonly),
        .cfg_mgmt_wr_rw1c_as_rw(cfg_mgmt_wr_rw1c_as_rw),
        .cfg_msg_data(cfg_msg_data),
        .cfg_msg_received(cfg_msg_received),
        .cfg_msg_received_assert_int_a(cfg_msg_received_assert_int_a),
        .cfg_msg_received_assert_int_b(cfg_msg_received_assert_int_b),
        .cfg_msg_received_assert_int_c(cfg_msg_received_assert_int_c),
        .cfg_msg_received_assert_int_d(cfg_msg_received_assert_int_d),
        .cfg_msg_received_deassert_int_a(cfg_msg_received_deassert_int_a),
        .cfg_msg_received_deassert_int_b(cfg_msg_received_deassert_int_b),
        .cfg_msg_received_deassert_int_c(cfg_msg_received_deassert_int_c),
        .cfg_msg_received_deassert_int_d(cfg_msg_received_deassert_int_d),
        .cfg_msg_received_err_cor(cfg_msg_received_err_cor),
        .cfg_msg_received_err_fatal(cfg_msg_received_err_fatal),
        .cfg_msg_received_err_non_fatal(cfg_msg_received_err_non_fatal),
        .cfg_msg_received_pm_as_nak(cfg_msg_received_pm_as_nak),
        .cfg_msg_received_pm_pme(cfg_msg_received_pm_pme),
        .cfg_msg_received_pme_to_ack(cfg_msg_received_pme_to_ack),
        .cfg_msg_received_setslotpowerlimit(cfg_msg_received_setslotpowerlimit),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pciecap_interrupt_msgnum(cfg_pciecap_interrupt_msgnum),
        .cfg_pm_force_state(cfg_pm_force_state),
        .cfg_pm_force_state_en(cfg_pm_force_state_en),
        .cfg_pm_halt_aspm_l0s(cfg_pm_halt_aspm_l0s),
        .cfg_pm_halt_aspm_l1(cfg_pm_halt_aspm_l1),
        .cfg_pm_send_pme_to(1'b0),
        .cfg_pm_wake(cfg_pm_wake),
        .cfg_pmcsr_pme_en(cfg_pmcsr_pme_en),
        .cfg_pmcsr_pme_status(cfg_pmcsr_pme_status),
        .cfg_pmcsr_powerstate(cfg_pmcsr_powerstate),
        .cfg_received_func_lvl_rst(cfg_received_func_lvl_rst),
        .cfg_rev_id_pf0({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .cfg_root_control_pme_int_en(cfg_root_control_pme_int_en),
        .cfg_root_control_syserr_corr_err_en(cfg_root_control_syserr_corr_err_en),
        .cfg_root_control_syserr_fatal_err_en(cfg_root_control_syserr_fatal_err_en),
        .cfg_root_control_syserr_non_fatal_err_en(cfg_root_control_syserr_non_fatal_err_en),
        .cfg_slot_control_electromech_il_ctl_pulse(cfg_slot_control_electromech_il_ctl_pulse),
        .cfg_status(NLW_inst_cfg_status_UNCONNECTED[15:0]),
        .cfg_subsys_id_pf0({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1}),
        .cfg_subsys_ven_id({1'b0,1'b0,1'b0,1'b1,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1,1'b0,1'b1,1'b1,1'b1,1'b0}),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_trn_pending(cfg_trn_pending),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .cfg_vc_tcvc_map(cfg_vc_tcvc_map),
        .cfg_ven_id({1'b0,1'b0,1'b0,1'b1,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1,1'b0,1'b1,1'b1,1'b1,1'b0}),
        .common_commands_in({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .common_commands_out(NLW_inst_common_commands_out_UNCONNECTED[11:0]),
        .ext_ch_gt_drpaddr({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .ext_ch_gt_drpclk(NLW_inst_ext_ch_gt_drpclk_UNCONNECTED),
        .ext_ch_gt_drpdi({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .ext_ch_gt_drpdo(NLW_inst_ext_ch_gt_drpdo_UNCONNECTED[15:0]),
        .ext_ch_gt_drpen(1'b0),
        .ext_ch_gt_drprdy(NLW_inst_ext_ch_gt_drprdy_UNCONNECTED[0]),
        .ext_ch_gt_drpwe(1'b0),
        .fc_cpld(fc_cpld),
        .fc_cplh(fc_cplh),
        .fc_npd(fc_npd),
        .fc_nph(fc_nph),
        .fc_pd(fc_pd),
        .fc_ph(fc_ph),
        .fc_sel(fc_sel),
        .gt_ch_drp_rdy(NLW_inst_gt_ch_drp_rdy_UNCONNECTED[0]),
        .icap_clk(1'b0),
        .icap_csib(1'b0),
        .icap_i({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .icap_o(NLW_inst_icap_o_UNCONNECTED[31:0]),
        .icap_rdwrb(1'b0),
        .int_dclk_out(NLW_inst_int_dclk_out_UNCONNECTED),
        .int_mmcm_lock_out(NLW_inst_int_mmcm_lock_out_UNCONNECTED),
        .int_oobclk_out(NLW_inst_int_oobclk_out_UNCONNECTED),
        .int_pclk_out_slave(NLW_inst_int_pclk_out_slave_UNCONNECTED),
        .int_pclk_sel_slave(1'b0),
        .int_pipe_rxusrclk_out(NLW_inst_int_pipe_rxusrclk_out_UNCONNECTED),
        .int_qplllock_out(NLW_inst_int_qplllock_out_UNCONNECTED[1:0]),
        .int_qplloutclk_out(NLW_inst_int_qplloutclk_out_UNCONNECTED[1:0]),
        .int_qplloutrefclk_out(NLW_inst_int_qplloutrefclk_out_UNCONNECTED[1:0]),
        .int_rxoutclk_out(NLW_inst_int_rxoutclk_out_UNCONNECTED[0]),
        .int_userclk1_out(NLW_inst_int_userclk1_out_UNCONNECTED),
        .int_userclk2_out(NLW_inst_int_userclk2_out_UNCONNECTED),
        .m_axis_rx_tdata(m_axis_rx_tdata),
        .m_axis_rx_tkeep({\^m_axis_rx_tkeep ,NLW_inst_m_axis_rx_tkeep_UNCONNECTED[3:0]}),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(\^m_axis_rx_tuser ),
        .m_axis_rx_tvalid(m_axis_rx_tvalid),
        .pci_exp_rxn(pci_exp_rxn),
        .pci_exp_rxp(pci_exp_rxp),
        .pci_exp_txn(pci_exp_txn),
        .pci_exp_txp(pci_exp_txp),
        .pcie_drp_addr(pcie_drp_addr),
        .pcie_drp_clk(pcie_drp_clk),
        .pcie_drp_di(pcie_drp_di),
        .pcie_drp_do(pcie_drp_do),
        .pcie_drp_en(pcie_drp_en),
        .pcie_drp_rdy(pcie_drp_rdy),
        .pcie_drp_we(pcie_drp_we),
        .pipe_cpll_lock(NLW_inst_pipe_cpll_lock_UNCONNECTED[0]),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_debug(NLW_inst_pipe_debug_UNCONNECTED[31:0]),
        .pipe_debug_0(NLW_inst_pipe_debug_0_UNCONNECTED[0]),
        .pipe_debug_1(NLW_inst_pipe_debug_1_UNCONNECTED[0]),
        .pipe_debug_2(NLW_inst_pipe_debug_2_UNCONNECTED[0]),
        .pipe_debug_3(NLW_inst_pipe_debug_3_UNCONNECTED[0]),
        .pipe_debug_4(NLW_inst_pipe_debug_4_UNCONNECTED[0]),
        .pipe_debug_5(NLW_inst_pipe_debug_5_UNCONNECTED[0]),
        .pipe_debug_6(NLW_inst_pipe_debug_6_UNCONNECTED[0]),
        .pipe_debug_7(NLW_inst_pipe_debug_7_UNCONNECTED[0]),
        .pipe_debug_8(NLW_inst_pipe_debug_8_UNCONNECTED[0]),
        .pipe_debug_9(NLW_inst_pipe_debug_9_UNCONNECTED[0]),
        .pipe_dmonitorout(NLW_inst_pipe_dmonitorout_UNCONNECTED[14:0]),
        .pipe_drp_fsm(NLW_inst_pipe_drp_fsm_UNCONNECTED[6:0]),
        .pipe_eyescandataerror(NLW_inst_pipe_eyescandataerror_UNCONNECTED[0]),
        .pipe_gen3_out(NLW_inst_pipe_gen3_out_UNCONNECTED),
        .pipe_loopback({1'b0,1'b0,1'b0}),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_mmcm_rst_n(1'b0),
        .pipe_oobclk_in(pipe_oobclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .pipe_qpll_lock(NLW_inst_pipe_qpll_lock_UNCONNECTED[0]),
        .pipe_qrst_fsm(NLW_inst_pipe_qrst_fsm_UNCONNECTED[11:0]),
        .pipe_qrst_idle(NLW_inst_pipe_qrst_idle_UNCONNECTED),
        .pipe_rate_fsm(NLW_inst_pipe_rate_fsm_UNCONNECTED[4:0]),
        .pipe_rate_idle(NLW_inst_pipe_rate_idle_UNCONNECTED),
        .pipe_rst_fsm(NLW_inst_pipe_rst_fsm_UNCONNECTED[4:0]),
        .pipe_rst_idle(NLW_inst_pipe_rst_idle_UNCONNECTED),
        .pipe_rx_0_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_1_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_2_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_3_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_4_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_5_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_6_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rx_7_sigs({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .pipe_rxbufstatus(NLW_inst_pipe_rxbufstatus_UNCONNECTED[2:0]),
        .pipe_rxcommadet(NLW_inst_pipe_rxcommadet_UNCONNECTED[0]),
        .pipe_rxdisperr(NLW_inst_pipe_rxdisperr_UNCONNECTED[7:0]),
        .pipe_rxdlysresetdone(NLW_inst_pipe_rxdlysresetdone_UNCONNECTED[0]),
        .pipe_rxnotintable(NLW_inst_pipe_rxnotintable_UNCONNECTED[7:0]),
        .pipe_rxoutclk_in(1'b0),
        .pipe_rxoutclk_out(pipe_rxoutclk_out),
        .pipe_rxphaligndone(NLW_inst_pipe_rxphaligndone_UNCONNECTED[0]),
        .pipe_rxpmaresetdone(NLW_inst_pipe_rxpmaresetdone_UNCONNECTED[0]),
        .pipe_rxprbscntreset(1'b0),
        .pipe_rxprbserr(NLW_inst_pipe_rxprbserr_UNCONNECTED[0]),
        .pipe_rxprbssel({1'b0,1'b0,1'b0}),
        .pipe_rxstatus(NLW_inst_pipe_rxstatus_UNCONNECTED[2:0]),
        .pipe_rxsyncdone(NLW_inst_pipe_rxsyncdone_UNCONNECTED[0]),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_sync_fsm_rx(NLW_inst_pipe_sync_fsm_rx_UNCONNECTED[6:0]),
        .pipe_sync_fsm_tx(NLW_inst_pipe_sync_fsm_tx_UNCONNECTED[5:0]),
        .pipe_tx_0_sigs(NLW_inst_pipe_tx_0_sigs_UNCONNECTED[24:0]),
        .pipe_tx_1_sigs(NLW_inst_pipe_tx_1_sigs_UNCONNECTED[24:0]),
        .pipe_tx_2_sigs(NLW_inst_pipe_tx_2_sigs_UNCONNECTED[24:0]),
        .pipe_tx_3_sigs(NLW_inst_pipe_tx_3_sigs_UNCONNECTED[24:0]),
        .pipe_tx_4_sigs(NLW_inst_pipe_tx_4_sigs_UNCONNECTED[24:0]),
        .pipe_tx_5_sigs(NLW_inst_pipe_tx_5_sigs_UNCONNECTED[24:0]),
        .pipe_tx_6_sigs(NLW_inst_pipe_tx_6_sigs_UNCONNECTED[24:0]),
        .pipe_tx_7_sigs(NLW_inst_pipe_tx_7_sigs_UNCONNECTED[24:0]),
        .pipe_txdlysresetdone(NLW_inst_pipe_txdlysresetdone_UNCONNECTED[0]),
        .pipe_txinhibit(1'b0),
        .pipe_txoutclk_out(pipe_txoutclk_out),
        .pipe_txphaligndone(NLW_inst_pipe_txphaligndone_UNCONNECTED[0]),
        .pipe_txphinitdone(NLW_inst_pipe_txphinitdone_UNCONNECTED[0]),
        .pipe_txprbsforceerr(1'b0),
        .pipe_txprbssel({1'b0,1'b0,1'b0}),
        .pipe_userclk1_in(pipe_userclk1_in),
        .pipe_userclk2_in(pipe_userclk2_in),
        .pl_directed_change_done(pl_directed_change_done),
        .pl_directed_link_auton(pl_directed_link_auton),
        .pl_directed_link_change(pl_directed_link_change),
        .pl_directed_link_speed(pl_directed_link_speed),
        .pl_directed_link_width(pl_directed_link_width),
        .pl_downstream_deemph_source(pl_downstream_deemph_source),
        .pl_initial_link_width(pl_initial_link_width),
        .pl_lane_reversal_mode(pl_lane_reversal_mode),
        .pl_link_gen2_cap(pl_link_gen2_cap),
        .pl_link_partner_gen2_supported(pl_link_partner_gen2_supported),
        .pl_link_upcfg_cap(pl_link_upcfg_cap),
        .pl_ltssm_state(pl_ltssm_state),
        .pl_phy_lnk_up(pl_phy_lnk_up),
        .pl_received_hot_rst(pl_received_hot_rst),
        .pl_rx_pm_state(pl_rx_pm_state),
        .pl_sel_lnk_rate(pl_sel_lnk_rate),
        .pl_sel_lnk_width(pl_sel_lnk_width),
        .pl_transmit_hot_rst(pl_transmit_hot_rst),
        .pl_tx_pm_state(pl_tx_pm_state),
        .pl_upstream_prefer_deemph(pl_upstream_prefer_deemph),
        .qpll_drp_clk(NLW_inst_qpll_drp_clk_UNCONNECTED),
        .qpll_drp_crscode({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .qpll_drp_done({1'b0,1'b0}),
        .qpll_drp_fsm({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .qpll_drp_gen3(NLW_inst_qpll_drp_gen3_UNCONNECTED),
        .qpll_drp_ovrd(NLW_inst_qpll_drp_ovrd_UNCONNECTED),
        .qpll_drp_reset({1'b0,1'b0}),
        .qpll_drp_rst_n(NLW_inst_qpll_drp_rst_n_UNCONNECTED),
        .qpll_drp_start(NLW_inst_qpll_drp_start_UNCONNECTED),
        .qpll_qplld(NLW_inst_qpll_qplld_UNCONNECTED),
        .qpll_qplllock({1'b0,1'b0}),
        .qpll_qplloutclk({1'b0,1'b0}),
        .qpll_qplloutrefclk({1'b0,1'b0}),
        .qpll_qpllreset(NLW_inst_qpll_qpllreset_UNCONNECTED[1:0]),
        .rx_np_ok(rx_np_ok),
        .rx_np_req(rx_np_req),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep({s_axis_tx_tkeep[7],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tready(s_axis_tx_tready),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .startup_cfgclk(NLW_inst_startup_cfgclk_UNCONNECTED),
        .startup_cfgmclk(NLW_inst_startup_cfgmclk_UNCONNECTED),
        .startup_clk(1'b0),
        .startup_eos(NLW_inst_startup_eos_UNCONNECTED),
        .startup_eos_in(1'b0),
        .startup_gsr(1'b0),
        .startup_gts(1'b0),
        .startup_keyclearb(1'b1),
        .startup_pack(1'b0),
        .startup_preq(NLW_inst_startup_preq_UNCONNECTED),
        .startup_usrcclko(1'b1),
        .startup_usrcclkts(1'b0),
        .startup_usrdoneo(1'b0),
        .startup_usrdonets(1'b1),
        .sys_clk(sys_clk),
        .sys_rst_n(sys_rst_n),
        .tx_buf_av(tx_buf_av),
        .tx_cfg_gnt(tx_cfg_gnt),
        .tx_cfg_req(tx_cfg_req),
        .tx_err_drop(tx_err_drop),
        .user_app_rdy(NLW_inst_user_app_rdy_UNCONNECTED),
        .user_clk_out(user_clk_out),
        .user_lnk_up(user_lnk_up),
        .user_reset_out(user_reset_out));
endmodule

module pcie_7x_bridge_axi_basic_rx
   (E,
    trn_rsrc_dsc_d,
    m_axis_rx_tvalid_reg,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
    trn_in_packet,
    reg_dsc_detect_reg,
    m_axis_rx_tuser,
    Q,
    SR,
    pipe_userclk2_in,
    trn_rrem,
    trn_rsrc_dsc,
    rsrc_rdy_filtered,
    trn_reof,
    trn_rsrc_dsc_prev0,
    trn_rsof,
    trn_recrc_err,
    trn_rerrfwd,
    trn_in_packet_reg,
    m_axis_rx_tready,
    dsc_detect,
    trn_rd,
    trn_rbar_hit);
  output [0:0]E;
  output trn_rsrc_dsc_d;
  output m_axis_rx_tvalid_reg;
  output [0:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output trn_in_packet;
  output reg_dsc_detect_reg;
  output [12:0]m_axis_rx_tuser;
  output [63:0]Q;
  input [0:0]SR;
  input pipe_userclk2_in;
  input [0:0]trn_rrem;
  input trn_rsrc_dsc;
  input rsrc_rdy_filtered;
  input trn_reof;
  input trn_rsrc_dsc_prev0;
  input trn_rsof;
  input trn_recrc_err;
  input trn_rerrfwd;
  input trn_in_packet_reg;
  input m_axis_rx_tready;
  input dsc_detect;
  input [63:0]trn_rd;
  input [6:0]trn_rbar_hit;

  wire [0:0]E;
  wire [63:0]Q;
  wire [0:0]SR;
  wire dsc_detect;
  wire [0:0]m_axis_rx_tkeep;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [12:0]m_axis_rx_tuser;
  wire m_axis_rx_tvalid_reg;
  wire [10:0]new_pkt_len;
  wire null_mux_sel;
  wire pipe_userclk2_in;
  wire reg_dsc_detect_reg;
  wire rsrc_rdy_filtered;
  wire rx_null_gen_inst_n_0;
  wire rx_null_gen_inst_n_1;
  wire rx_null_gen_inst_n_2;
  wire rx_null_gen_inst_n_3;
  wire rx_null_gen_inst_n_4;
  wire rx_null_gen_inst_n_5;
  wire rx_null_gen_inst_n_6;
  wire rx_null_gen_inst_n_7;
  wire rx_null_gen_inst_n_8;
  wire rx_pipeline_inst_n_73;
  wire rx_pipeline_inst_n_74;
  wire rx_pipeline_inst_n_8;
  wire trn_in_packet;
  wire trn_in_packet_reg;
  wire [6:0]trn_rbar_hit;
  wire [63:0]trn_rd;
  wire trn_recrc_err;
  wire trn_reof;
  wire trn_rerrfwd;
  wire [0:0]trn_rrem;
  wire trn_rsof;
  wire trn_rsrc_dsc;
  wire trn_rsrc_dsc_d;
  wire trn_rsrc_dsc_prev0;

  pcie_7x_bridge_axi_basic_rx_null_gen rx_null_gen_inst
       (.D({rx_null_gen_inst_n_0,rx_null_gen_inst_n_1}),
        .Q({Q[30:29],Q[15],Q[1:0]}),
        .S({rx_null_gen_inst_n_7,rx_null_gen_inst_n_8}),
        .SR(SR),
        .cur_state_reg_0(m_axis_rx_tvalid_reg),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(m_axis_rx_tuser[12]),
        .\m_axis_rx_tuser_reg[19] (rx_pipeline_inst_n_74),
        .\m_axis_rx_tuser_reg[21] (rx_pipeline_inst_n_73),
        .new_pkt_len(new_pkt_len),
        .null_mux_sel(null_mux_sel),
        .null_mux_sel_reg(rx_null_gen_inst_n_5),
        .null_mux_sel_reg_0(rx_null_gen_inst_n_6),
        .null_mux_sel_reg_1(rx_pipeline_inst_n_8),
        .pipe_userclk2_in(pipe_userclk2_in),
        .\reg_pkt_len_counter_reg[0]_0 (rx_null_gen_inst_n_4),
        .\reg_pkt_len_counter_reg[3]_0 (rx_null_gen_inst_n_3),
        .\reg_tkeep[7]_i_7_0 (rx_null_gen_inst_n_2));
  pcie_7x_bridge_axi_basic_rx_pipeline rx_pipeline_inst
       (.D({rx_null_gen_inst_n_0,rx_null_gen_inst_n_1}),
        .E(E),
        .Q(Q),
        .S({rx_null_gen_inst_n_7,rx_null_gen_inst_n_8}),
        .SR(SR),
        .dsc_detect(dsc_detect),
        .m_axis_rx_tkeep(m_axis_rx_tkeep),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(m_axis_rx_tuser),
        .m_axis_rx_tvalid_reg_0(m_axis_rx_tvalid_reg),
        .new_pkt_len(new_pkt_len),
        .null_mux_sel(null_mux_sel),
        .null_mux_sel_reg_0(rx_null_gen_inst_n_5),
        .pcie_block_i(rx_pipeline_inst_n_73),
        .pcie_block_i_0(rx_pipeline_inst_n_74),
        .pipe_userclk2_in(pipe_userclk2_in),
        .reg_dsc_detect_reg_0(reg_dsc_detect_reg),
        .\reg_tkeep_reg[7]_0 (rx_null_gen_inst_n_3),
        .reg_tlast_reg_0(rx_null_gen_inst_n_6),
        .rsrc_rdy_filtered(rsrc_rdy_filtered),
        .trn_in_packet(trn_in_packet),
        .trn_in_packet_reg_0(trn_in_packet_reg),
        .trn_rbar_hit(trn_rbar_hit),
        .trn_rd(trn_rd),
        .trn_rdst_rdy_reg_0(rx_null_gen_inst_n_2),
        .trn_rdst_rdy_reg_1(rx_null_gen_inst_n_4),
        .trn_recrc_err(trn_recrc_err),
        .trn_reof(trn_reof),
        .trn_rerrfwd(trn_rerrfwd),
        .trn_rrem(trn_rrem),
        .trn_rsof(trn_rsof),
        .trn_rsrc_dsc(trn_rsrc_dsc),
        .trn_rsrc_dsc_d(trn_rsrc_dsc_d),
        .trn_rsrc_dsc_prev0(trn_rsrc_dsc_prev0),
        .user_reset_out_reg(rx_pipeline_inst_n_8));
endmodule

module pcie_7x_bridge_axi_basic_rx_null_gen
   (D,
    \reg_tkeep[7]_i_7_0 ,
    \reg_pkt_len_counter_reg[3]_0 ,
    \reg_pkt_len_counter_reg[0]_0 ,
    null_mux_sel_reg,
    null_mux_sel_reg_0,
    S,
    SR,
    pipe_userclk2_in,
    null_mux_sel,
    \m_axis_rx_tuser_reg[19] ,
    new_pkt_len,
    m_axis_rx_tready,
    null_mux_sel_reg_1,
    cur_state_reg_0,
    m_axis_rx_tuser,
    \m_axis_rx_tuser_reg[21] ,
    Q);
  output [1:0]D;
  output \reg_tkeep[7]_i_7_0 ;
  output \reg_pkt_len_counter_reg[3]_0 ;
  output \reg_pkt_len_counter_reg[0]_0 ;
  output null_mux_sel_reg;
  output null_mux_sel_reg_0;
  output [1:0]S;
  input [0:0]SR;
  input pipe_userclk2_in;
  input null_mux_sel;
  input \m_axis_rx_tuser_reg[19] ;
  input [10:0]new_pkt_len;
  input m_axis_rx_tready;
  input null_mux_sel_reg_1;
  input cur_state_reg_0;
  input [0:0]m_axis_rx_tuser;
  input \m_axis_rx_tuser_reg[21] ;
  input [4:0]Q;

  wire [1:0]D;
  wire [4:0]Q;
  wire [1:0]S;
  wire [0:0]SR;
  wire cur_state;
  wire cur_state_reg_0;
  wire m_axis_rx_tready;
  wire [0:0]m_axis_rx_tuser;
  wire \m_axis_rx_tuser_reg[19] ;
  wire \m_axis_rx_tuser_reg[21] ;
  wire [10:0]new_pkt_len;
  wire next_state;
  wire null_mux_sel;
  wire null_mux_sel_reg;
  wire null_mux_sel_reg_0;
  wire null_mux_sel_reg_1;
  wire pipe_userclk2_in;
  wire [11:1]pkt_len_counter;
  wire [1:0]pkt_len_counter_0;
  wire pkt_len_counter_dec__0_carry__0_i_1_n_0;
  wire pkt_len_counter_dec__0_carry__0_i_2_n_0;
  wire pkt_len_counter_dec__0_carry__0_i_3_n_0;
  wire pkt_len_counter_dec__0_carry__0_i_4_n_0;
  wire pkt_len_counter_dec__0_carry__0_n_0;
  wire pkt_len_counter_dec__0_carry__0_n_1;
  wire pkt_len_counter_dec__0_carry__0_n_2;
  wire pkt_len_counter_dec__0_carry__0_n_3;
  wire pkt_len_counter_dec__0_carry__1_i_1_n_0;
  wire pkt_len_counter_dec__0_carry__1_i_2_n_0;
  wire pkt_len_counter_dec__0_carry__1_i_3_n_0;
  wire pkt_len_counter_dec__0_carry__1_n_2;
  wire pkt_len_counter_dec__0_carry__1_n_3;
  wire pkt_len_counter_dec__0_carry_i_1_n_0;
  wire pkt_len_counter_dec__0_carry_i_2_n_0;
  wire pkt_len_counter_dec__0_carry_i_3_n_0;
  wire pkt_len_counter_dec__0_carry_i_4_n_0;
  wire pkt_len_counter_dec__0_carry_i_5_n_0;
  wire pkt_len_counter_dec__0_carry_n_0;
  wire pkt_len_counter_dec__0_carry_n_1;
  wire pkt_len_counter_dec__0_carry_n_2;
  wire pkt_len_counter_dec__0_carry_n_3;
  wire [11:0]reg_pkt_len_counter;
  wire \reg_pkt_len_counter[11]_i_2_n_0 ;
  wire \reg_pkt_len_counter[11]_i_3_n_0 ;
  wire \reg_pkt_len_counter[11]_i_4_n_0 ;
  wire \reg_pkt_len_counter_reg[0]_0 ;
  wire \reg_pkt_len_counter_reg[3]_0 ;
  wire \reg_tkeep[7]_i_4_n_0 ;
  wire \reg_tkeep[7]_i_5_n_0 ;
  wire \reg_tkeep[7]_i_6_n_0 ;
  wire \reg_tkeep[7]_i_7_0 ;
  wire \reg_tkeep[7]_i_7_n_0 ;
  wire [11:2]sel0;
  wire [3:2]NLW_pkt_len_counter_dec__0_carry__1_CO_UNCONNECTED;
  wire [3:3]NLW_pkt_len_counter_dec__0_carry__1_O_UNCONNECTED;

  LUT5 #(
    .INIT(32'hAAAAAAEA)) 
    cur_state_i_1
       (.I0(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I1(m_axis_rx_tready),
        .I2(cur_state_reg_0),
        .I3(cur_state),
        .I4(m_axis_rx_tuser),
        .O(next_state));
  FDRE cur_state_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(next_state),
        .Q(cur_state),
        .R(SR));
  LUT6 #(
    .INIT(64'h5555555500000400)) 
    \m_axis_rx_tuser[19]_i_1 
       (.I0(SR),
        .I1(\reg_tkeep[7]_i_7_0 ),
        .I2(\reg_pkt_len_counter_reg[3]_0 ),
        .I3(null_mux_sel),
        .I4(pkt_len_counter_0[0]),
        .I5(\m_axis_rx_tuser_reg[19] ),
        .O(D[0]));
  LUT6 #(
    .INIT(64'h00000000FF80FF08)) 
    \m_axis_rx_tuser[21]_i_2 
       (.I0(\reg_tkeep[7]_i_7_0 ),
        .I1(null_mux_sel),
        .I2(\reg_pkt_len_counter_reg[3]_0 ),
        .I3(\m_axis_rx_tuser_reg[21] ),
        .I4(pkt_len_counter_0[0]),
        .I5(SR),
        .O(D[1]));
  LUT6 #(
    .INIT(64'h0000000077F7FFFF)) 
    null_mux_sel_i_1
       (.I0(\reg_tkeep[7]_i_7_0 ),
        .I1(null_mux_sel),
        .I2(pkt_len_counter_0[0]),
        .I3(\reg_pkt_len_counter_reg[3]_0 ),
        .I4(m_axis_rx_tready),
        .I5(null_mux_sel_reg_1),
        .O(null_mux_sel_reg));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 pkt_len_counter_dec__0_carry
       (.CI(1'b0),
        .CO({pkt_len_counter_dec__0_carry_n_0,pkt_len_counter_dec__0_carry_n_1,pkt_len_counter_dec__0_carry_n_2,pkt_len_counter_dec__0_carry_n_3}),
        .CYINIT(1'b0),
        .DI({reg_pkt_len_counter[3:2],pkt_len_counter_dec__0_carry_i_1_n_0,1'b0}),
        .O(pkt_len_counter[4:1]),
        .S({pkt_len_counter_dec__0_carry_i_2_n_0,pkt_len_counter_dec__0_carry_i_3_n_0,pkt_len_counter_dec__0_carry_i_4_n_0,pkt_len_counter_dec__0_carry_i_5_n_0}));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 pkt_len_counter_dec__0_carry__0
       (.CI(pkt_len_counter_dec__0_carry_n_0),
        .CO({pkt_len_counter_dec__0_carry__0_n_0,pkt_len_counter_dec__0_carry__0_n_1,pkt_len_counter_dec__0_carry__0_n_2,pkt_len_counter_dec__0_carry__0_n_3}),
        .CYINIT(1'b0),
        .DI(reg_pkt_len_counter[7:4]),
        .O(pkt_len_counter[8:5]),
        .S({pkt_len_counter_dec__0_carry__0_i_1_n_0,pkt_len_counter_dec__0_carry__0_i_2_n_0,pkt_len_counter_dec__0_carry__0_i_3_n_0,pkt_len_counter_dec__0_carry__0_i_4_n_0}));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__0_i_1
       (.I0(reg_pkt_len_counter[7]),
        .I1(reg_pkt_len_counter[8]),
        .O(pkt_len_counter_dec__0_carry__0_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__0_i_2
       (.I0(reg_pkt_len_counter[6]),
        .I1(reg_pkt_len_counter[7]),
        .O(pkt_len_counter_dec__0_carry__0_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__0_i_3
       (.I0(reg_pkt_len_counter[5]),
        .I1(reg_pkt_len_counter[6]),
        .O(pkt_len_counter_dec__0_carry__0_i_3_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__0_i_4
       (.I0(reg_pkt_len_counter[4]),
        .I1(reg_pkt_len_counter[5]),
        .O(pkt_len_counter_dec__0_carry__0_i_4_n_0));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 pkt_len_counter_dec__0_carry__1
       (.CI(pkt_len_counter_dec__0_carry__0_n_0),
        .CO({NLW_pkt_len_counter_dec__0_carry__1_CO_UNCONNECTED[3:2],pkt_len_counter_dec__0_carry__1_n_2,pkt_len_counter_dec__0_carry__1_n_3}),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,reg_pkt_len_counter[9:8]}),
        .O({NLW_pkt_len_counter_dec__0_carry__1_O_UNCONNECTED[3],pkt_len_counter[11:9]}),
        .S({1'b0,pkt_len_counter_dec__0_carry__1_i_1_n_0,pkt_len_counter_dec__0_carry__1_i_2_n_0,pkt_len_counter_dec__0_carry__1_i_3_n_0}));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__1_i_1
       (.I0(reg_pkt_len_counter[10]),
        .I1(reg_pkt_len_counter[11]),
        .O(pkt_len_counter_dec__0_carry__1_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__1_i_2
       (.I0(reg_pkt_len_counter[9]),
        .I1(reg_pkt_len_counter[10]),
        .O(pkt_len_counter_dec__0_carry__1_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry__1_i_3
       (.I0(reg_pkt_len_counter[8]),
        .I1(reg_pkt_len_counter[9]),
        .O(pkt_len_counter_dec__0_carry__1_i_3_n_0));
  LUT2 #(
    .INIT(4'hB)) 
    pkt_len_counter_dec__0_carry_i_1
       (.I0(reg_pkt_len_counter[1]),
        .I1(m_axis_rx_tready),
        .O(pkt_len_counter_dec__0_carry_i_1_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry_i_2
       (.I0(reg_pkt_len_counter[3]),
        .I1(reg_pkt_len_counter[4]),
        .O(pkt_len_counter_dec__0_carry_i_2_n_0));
  LUT2 #(
    .INIT(4'h9)) 
    pkt_len_counter_dec__0_carry_i_3
       (.I0(reg_pkt_len_counter[2]),
        .I1(reg_pkt_len_counter[3]),
        .O(pkt_len_counter_dec__0_carry_i_3_n_0));
  LUT3 #(
    .INIT(8'hD2)) 
    pkt_len_counter_dec__0_carry_i_4
       (.I0(m_axis_rx_tready),
        .I1(reg_pkt_len_counter[1]),
        .I2(reg_pkt_len_counter[2]),
        .O(pkt_len_counter_dec__0_carry_i_4_n_0));
  LUT2 #(
    .INIT(4'h6)) 
    pkt_len_counter_dec__0_carry_i_5
       (.I0(reg_pkt_len_counter[1]),
        .I1(m_axis_rx_tready),
        .O(pkt_len_counter_dec__0_carry_i_5_n_0));
  (* SOFT_HLUTNM = "soft_lutpair66" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[0]_i_1 
       (.I0(reg_pkt_len_counter[0]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[0]),
        .O(pkt_len_counter_0[0]));
  (* SOFT_HLUTNM = "soft_lutpair63" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[10]_i_1 
       (.I0(pkt_len_counter[10]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[10]),
        .O(sel0[10]));
  (* SOFT_HLUTNM = "soft_lutpair63" *) 
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[11]_i_1 
       (.I0(pkt_len_counter[11]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .O(sel0[11]));
  LUT6 #(
    .INIT(64'hAAAAAAA8AAAAAAAA)) 
    \reg_pkt_len_counter[11]_i_2 
       (.I0(cur_state),
        .I1(reg_pkt_len_counter[3]),
        .I2(reg_pkt_len_counter[8]),
        .I3(reg_pkt_len_counter[7]),
        .I4(\reg_pkt_len_counter[11]_i_3_n_0 ),
        .I5(\reg_pkt_len_counter[11]_i_4_n_0 ),
        .O(\reg_pkt_len_counter[11]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'hFFEF)) 
    \reg_pkt_len_counter[11]_i_3 
       (.I0(reg_pkt_len_counter[5]),
        .I1(reg_pkt_len_counter[4]),
        .I2(m_axis_rx_tready),
        .I3(reg_pkt_len_counter[9]),
        .O(\reg_pkt_len_counter[11]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h0000000000000007)) 
    \reg_pkt_len_counter[11]_i_4 
       (.I0(reg_pkt_len_counter[0]),
        .I1(reg_pkt_len_counter[1]),
        .I2(reg_pkt_len_counter[2]),
        .I3(reg_pkt_len_counter[6]),
        .I4(reg_pkt_len_counter[10]),
        .I5(reg_pkt_len_counter[11]),
        .O(\reg_pkt_len_counter[11]_i_4_n_0 ));
  LUT3 #(
    .INIT(8'hE2)) 
    \reg_pkt_len_counter[1]_i_1 
       (.I0(new_pkt_len[1]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(pkt_len_counter[1]),
        .O(pkt_len_counter_0[1]));
  (* SOFT_HLUTNM = "soft_lutpair62" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[2]_i_1 
       (.I0(pkt_len_counter[2]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[2]),
        .O(sel0[2]));
  (* SOFT_HLUTNM = "soft_lutpair66" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[3]_i_1 
       (.I0(pkt_len_counter[3]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[3]),
        .O(sel0[3]));
  LUT4 #(
    .INIT(16'h1EEE)) 
    \reg_pkt_len_counter[3]_i_7 
       (.I0(Q[2]),
        .I1(Q[3]),
        .I2(Q[1]),
        .I3(Q[4]),
        .O(S[1]));
  LUT4 #(
    .INIT(16'h6999)) 
    \reg_pkt_len_counter[3]_i_8 
       (.I0(Q[3]),
        .I1(Q[2]),
        .I2(Q[4]),
        .I3(Q[0]),
        .O(S[0]));
  (* SOFT_HLUTNM = "soft_lutpair60" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[4]_i_1 
       (.I0(pkt_len_counter[4]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[4]),
        .O(sel0[4]));
  (* SOFT_HLUTNM = "soft_lutpair64" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[5]_i_1 
       (.I0(pkt_len_counter[5]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[5]),
        .O(sel0[5]));
  (* SOFT_HLUTNM = "soft_lutpair61" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[6]_i_1 
       (.I0(pkt_len_counter[6]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[6]),
        .O(sel0[6]));
  (* SOFT_HLUTNM = "soft_lutpair65" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[7]_i_1 
       (.I0(pkt_len_counter[7]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[7]),
        .O(sel0[7]));
  (* SOFT_HLUTNM = "soft_lutpair59" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[8]_i_1 
       (.I0(pkt_len_counter[8]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[8]),
        .O(sel0[8]));
  (* SOFT_HLUTNM = "soft_lutpair64" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \reg_pkt_len_counter[9]_i_1 
       (.I0(pkt_len_counter[9]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[9]),
        .O(sel0[9]));
  FDRE \reg_pkt_len_counter_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(pkt_len_counter_0[0]),
        .Q(reg_pkt_len_counter[0]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[10] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[10]),
        .Q(reg_pkt_len_counter[10]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[11] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[11]),
        .Q(reg_pkt_len_counter[11]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(pkt_len_counter_0[1]),
        .Q(reg_pkt_len_counter[1]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[2]),
        .Q(reg_pkt_len_counter[2]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[3]),
        .Q(reg_pkt_len_counter[3]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[4]),
        .Q(reg_pkt_len_counter[4]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[5]),
        .Q(reg_pkt_len_counter[5]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[6]),
        .Q(reg_pkt_len_counter[6]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[7]),
        .Q(reg_pkt_len_counter[7]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[8] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[8]),
        .Q(reg_pkt_len_counter[8]),
        .R(SR));
  FDRE \reg_pkt_len_counter_reg[9] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(sel0[9]),
        .Q(reg_pkt_len_counter[9]),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000000000000001)) 
    \reg_tkeep[7]_i_2 
       (.I0(sel0[11]),
        .I1(sel0[10]),
        .I2(\reg_tkeep[7]_i_4_n_0 ),
        .I3(\reg_tkeep[7]_i_5_n_0 ),
        .I4(\reg_tkeep[7]_i_6_n_0 ),
        .I5(\reg_tkeep[7]_i_7_n_0 ),
        .O(\reg_tkeep[7]_i_7_0 ));
  (* SOFT_HLUTNM = "soft_lutpair65" *) 
  LUT3 #(
    .INIT(8'h47)) 
    \reg_tkeep[7]_i_3 
       (.I0(pkt_len_counter[1]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[1]),
        .O(\reg_pkt_len_counter_reg[3]_0 ));
  (* SOFT_HLUTNM = "soft_lutpair59" *) 
  LUT5 #(
    .INIT(32'hFFFACCFA)) 
    \reg_tkeep[7]_i_4 
       (.I0(new_pkt_len[8]),
        .I1(pkt_len_counter[8]),
        .I2(new_pkt_len[9]),
        .I3(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I4(pkt_len_counter[9]),
        .O(\reg_tkeep[7]_i_4_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair61" *) 
  LUT5 #(
    .INIT(32'hFFFACCFA)) 
    \reg_tkeep[7]_i_5 
       (.I0(new_pkt_len[6]),
        .I1(pkt_len_counter[6]),
        .I2(new_pkt_len[7]),
        .I3(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I4(pkt_len_counter[7]),
        .O(\reg_tkeep[7]_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair60" *) 
  LUT5 #(
    .INIT(32'hFFFACCFA)) 
    \reg_tkeep[7]_i_6 
       (.I0(new_pkt_len[4]),
        .I1(pkt_len_counter[4]),
        .I2(new_pkt_len[5]),
        .I3(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I4(pkt_len_counter[5]),
        .O(\reg_tkeep[7]_i_6_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair62" *) 
  LUT5 #(
    .INIT(32'hFFFACCFA)) 
    \reg_tkeep[7]_i_7 
       (.I0(new_pkt_len[2]),
        .I1(pkt_len_counter[2]),
        .I2(new_pkt_len[3]),
        .I3(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I4(pkt_len_counter[3]),
        .O(\reg_tkeep[7]_i_7_n_0 ));
  LUT5 #(
    .INIT(32'hFFFFB000)) 
    reg_tlast_i_1
       (.I0(\reg_pkt_len_counter_reg[3]_0 ),
        .I1(pkt_len_counter_0[0]),
        .I2(null_mux_sel),
        .I3(\reg_tkeep[7]_i_7_0 ),
        .I4(\m_axis_rx_tuser_reg[21] ),
        .O(null_mux_sel_reg_0));
  LUT6 #(
    .INIT(64'hB8308800FFFFFFFF)) 
    trn_rdst_rdy_i_3
       (.I0(pkt_len_counter[1]),
        .I1(\reg_pkt_len_counter[11]_i_2_n_0 ),
        .I2(new_pkt_len[1]),
        .I3(reg_pkt_len_counter[0]),
        .I4(new_pkt_len[0]),
        .I5(null_mux_sel),
        .O(\reg_pkt_len_counter_reg[0]_0 ));
endmodule

module pcie_7x_bridge_axi_basic_rx_pipeline
   (E,
    trn_rsrc_dsc_d,
    m_axis_rx_tvalid_reg_0,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
    null_mux_sel,
    trn_in_packet,
    reg_dsc_detect_reg_0,
    user_reset_out_reg,
    Q,
    pcie_block_i,
    pcie_block_i_0,
    new_pkt_len,
    m_axis_rx_tuser,
    SR,
    pipe_userclk2_in,
    trn_rrem,
    trn_rsrc_dsc,
    rsrc_rdy_filtered,
    trn_reof,
    reg_tlast_reg_0,
    trn_rsrc_dsc_prev0,
    trn_rsof,
    trn_recrc_err,
    trn_rerrfwd,
    null_mux_sel_reg_0,
    trn_in_packet_reg_0,
    m_axis_rx_tready,
    dsc_detect,
    trn_rdst_rdy_reg_0,
    trn_rdst_rdy_reg_1,
    \reg_tkeep_reg[7]_0 ,
    trn_rd,
    trn_rbar_hit,
    S,
    D);
  output [0:0]E;
  output trn_rsrc_dsc_d;
  output m_axis_rx_tvalid_reg_0;
  output [0:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output null_mux_sel;
  output trn_in_packet;
  output reg_dsc_detect_reg_0;
  output user_reset_out_reg;
  output [63:0]Q;
  output pcie_block_i;
  output pcie_block_i_0;
  output [10:0]new_pkt_len;
  output [12:0]m_axis_rx_tuser;
  input [0:0]SR;
  input pipe_userclk2_in;
  input [0:0]trn_rrem;
  input trn_rsrc_dsc;
  input rsrc_rdy_filtered;
  input trn_reof;
  input reg_tlast_reg_0;
  input trn_rsrc_dsc_prev0;
  input trn_rsof;
  input trn_recrc_err;
  input trn_rerrfwd;
  input null_mux_sel_reg_0;
  input trn_in_packet_reg_0;
  input m_axis_rx_tready;
  input dsc_detect;
  input trn_rdst_rdy_reg_0;
  input trn_rdst_rdy_reg_1;
  input \reg_tkeep_reg[7]_0 ;
  input [63:0]trn_rd;
  input [6:0]trn_rbar_hit;
  input [1:0]S;
  input [1:0]D;

  wire [1:0]D;
  wire [0:0]E;
  wire [63:0]Q;
  wire [1:0]S;
  wire [0:0]SR;
  wire data_hold;
  wire data_prev;
  wire dsc_detect;
  wire \m_axis_rx_tdata[63]_i_1_n_0 ;
  wire [0:0]m_axis_rx_tkeep;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [12:0]m_axis_rx_tuser;
  wire \m_axis_rx_tuser[0]_i_1_n_0 ;
  wire \m_axis_rx_tuser[14]_i_1_n_0 ;
  wire \m_axis_rx_tuser[14]_i_2_n_0 ;
  wire \m_axis_rx_tuser[18]_i_1_n_0 ;
  wire \m_axis_rx_tuser[1]_i_1_n_0 ;
  wire \m_axis_rx_tuser[21]_i_1_n_0 ;
  wire \m_axis_rx_tuser[2]_i_1_n_0 ;
  wire \m_axis_rx_tuser[3]_i_1_n_0 ;
  wire \m_axis_rx_tuser[4]_i_1_n_0 ;
  wire \m_axis_rx_tuser[5]_i_1_n_0 ;
  wire \m_axis_rx_tuser[6]_i_1_n_0 ;
  wire \m_axis_rx_tuser[7]_i_1_n_0 ;
  wire \m_axis_rx_tuser[8]_i_1_n_0 ;
  wire m_axis_rx_tvalid_i_1_n_0;
  wire m_axis_rx_tvalid_reg_0;
  wire [10:0]new_pkt_len;
  wire null_mux_sel;
  wire null_mux_sel_reg_0;
  wire [63:0]p_1_in;
  wire [1:0]packet_overhead;
  wire pcie_block_i;
  wire pcie_block_i_0;
  wire pipe_userclk2_in;
  wire reg_dsc_detect_i_1_n_0;
  wire reg_dsc_detect_reg_0;
  wire \reg_pkt_len_counter[10]_i_3_n_0 ;
  wire \reg_pkt_len_counter[10]_i_4_n_0 ;
  wire \reg_pkt_len_counter[3]_i_5_n_0 ;
  wire \reg_pkt_len_counter[3]_i_6_n_0 ;
  wire \reg_pkt_len_counter[7]_i_3_n_0 ;
  wire \reg_pkt_len_counter[7]_i_4_n_0 ;
  wire \reg_pkt_len_counter[7]_i_5_n_0 ;
  wire \reg_pkt_len_counter[7]_i_6_n_0 ;
  wire \reg_pkt_len_counter_reg[10]_i_2_n_3 ;
  wire \reg_pkt_len_counter_reg[3]_i_2_n_0 ;
  wire \reg_pkt_len_counter_reg[3]_i_2_n_1 ;
  wire \reg_pkt_len_counter_reg[3]_i_2_n_2 ;
  wire \reg_pkt_len_counter_reg[3]_i_2_n_3 ;
  wire \reg_pkt_len_counter_reg[7]_i_2_n_0 ;
  wire \reg_pkt_len_counter_reg[7]_i_2_n_1 ;
  wire \reg_pkt_len_counter_reg[7]_i_2_n_2 ;
  wire \reg_pkt_len_counter_reg[7]_i_2_n_3 ;
  wire [7:7]reg_tkeep;
  wire \reg_tkeep_reg[7]_0 ;
  wire reg_tlast_reg_0;
  wire rsrc_rdy_filtered;
  wire trn_in_packet;
  wire trn_in_packet_reg_0;
  wire [6:0]trn_rbar_hit;
  wire [6:0]trn_rbar_hit_prev;
  wire [63:0]trn_rd;
  wire [63:0]trn_rd_prev;
  wire trn_rdst_rdy_i_1_n_0;
  wire trn_rdst_rdy_i_2_n_0;
  wire trn_rdst_rdy_reg_0;
  wire trn_rdst_rdy_reg_1;
  wire trn_recrc_err;
  wire trn_recrc_err_prev;
  wire trn_reof;
  wire trn_reof_prev;
  wire trn_rerrfwd;
  wire trn_rerrfwd_prev;
  wire [0:0]trn_rrem;
  wire trn_rrem_prev;
  wire trn_rsof;
  wire trn_rsof_prev;
  wire trn_rsrc_dsc;
  wire trn_rsrc_dsc_d;
  wire trn_rsrc_dsc_prev;
  wire trn_rsrc_dsc_prev0;
  wire trn_rsrc_rdy_prev;
  wire user_reset_out_reg;
  wire [3:1]\NLW_reg_pkt_len_counter_reg[10]_i_2_CO_UNCONNECTED ;
  wire [3:2]\NLW_reg_pkt_len_counter_reg[10]_i_2_O_UNCONNECTED ;

  LUT2 #(
    .INIT(4'h2)) 
    data_prev_i_1
       (.I0(m_axis_rx_tvalid_reg_0),
        .I1(m_axis_rx_tready),
        .O(data_hold));
  FDRE data_prev_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(data_hold),
        .Q(data_prev),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair95" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[0]_i_1 
       (.I0(trn_rd_prev[0]),
        .I1(data_prev),
        .I2(trn_rd[32]),
        .O(p_1_in[0]));
  (* SOFT_HLUTNM = "soft_lutpair98" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[10]_i_1 
       (.I0(trn_rd_prev[10]),
        .I1(data_prev),
        .I2(trn_rd[42]),
        .O(p_1_in[10]));
  (* SOFT_HLUTNM = "soft_lutpair96" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[11]_i_1 
       (.I0(trn_rd_prev[11]),
        .I1(data_prev),
        .I2(trn_rd[43]),
        .O(p_1_in[11]));
  (* SOFT_HLUTNM = "soft_lutpair92" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[12]_i_1 
       (.I0(trn_rd_prev[12]),
        .I1(data_prev),
        .I2(trn_rd[44]),
        .O(p_1_in[12]));
  (* SOFT_HLUTNM = "soft_lutpair91" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[13]_i_1 
       (.I0(trn_rd_prev[13]),
        .I1(data_prev),
        .I2(trn_rd[45]),
        .O(p_1_in[13]));
  (* SOFT_HLUTNM = "soft_lutpair101" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[14]_i_1 
       (.I0(trn_rd_prev[14]),
        .I1(data_prev),
        .I2(trn_rd[46]),
        .O(p_1_in[14]));
  (* SOFT_HLUTNM = "soft_lutpair93" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[15]_i_1 
       (.I0(trn_rd_prev[15]),
        .I1(data_prev),
        .I2(trn_rd[47]),
        .O(p_1_in[15]));
  (* SOFT_HLUTNM = "soft_lutpair90" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[16]_i_1 
       (.I0(trn_rd_prev[16]),
        .I1(data_prev),
        .I2(trn_rd[48]),
        .O(p_1_in[16]));
  (* SOFT_HLUTNM = "soft_lutpair86" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[17]_i_1 
       (.I0(trn_rd_prev[17]),
        .I1(data_prev),
        .I2(trn_rd[49]),
        .O(p_1_in[17]));
  (* SOFT_HLUTNM = "soft_lutpair84" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[18]_i_1 
       (.I0(trn_rd_prev[18]),
        .I1(data_prev),
        .I2(trn_rd[50]),
        .O(p_1_in[18]));
  (* SOFT_HLUTNM = "soft_lutpair98" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[19]_i_1 
       (.I0(trn_rd_prev[19]),
        .I1(data_prev),
        .I2(trn_rd[51]),
        .O(p_1_in[19]));
  (* SOFT_HLUTNM = "soft_lutpair101" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[1]_i_1 
       (.I0(trn_rd_prev[1]),
        .I1(data_prev),
        .I2(trn_rd[33]),
        .O(p_1_in[1]));
  (* SOFT_HLUTNM = "soft_lutpair94" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[20]_i_1 
       (.I0(trn_rd_prev[20]),
        .I1(data_prev),
        .I2(trn_rd[52]),
        .O(p_1_in[20]));
  (* SOFT_HLUTNM = "soft_lutpair88" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[21]_i_1 
       (.I0(trn_rd_prev[21]),
        .I1(data_prev),
        .I2(trn_rd[53]),
        .O(p_1_in[21]));
  (* SOFT_HLUTNM = "soft_lutpair97" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[22]_i_1 
       (.I0(trn_rd_prev[22]),
        .I1(data_prev),
        .I2(trn_rd[54]),
        .O(p_1_in[22]));
  (* SOFT_HLUTNM = "soft_lutpair99" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[23]_i_1 
       (.I0(trn_rd_prev[23]),
        .I1(data_prev),
        .I2(trn_rd[55]),
        .O(p_1_in[23]));
  (* SOFT_HLUTNM = "soft_lutpair94" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[24]_i_1 
       (.I0(trn_rd_prev[24]),
        .I1(data_prev),
        .I2(trn_rd[56]),
        .O(p_1_in[24]));
  (* SOFT_HLUTNM = "soft_lutpair82" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[25]_i_1 
       (.I0(trn_rd_prev[25]),
        .I1(data_prev),
        .I2(trn_rd[57]),
        .O(p_1_in[25]));
  (* SOFT_HLUTNM = "soft_lutpair81" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[26]_i_1 
       (.I0(trn_rd_prev[26]),
        .I1(data_prev),
        .I2(trn_rd[58]),
        .O(p_1_in[26]));
  (* SOFT_HLUTNM = "soft_lutpair83" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[27]_i_1 
       (.I0(trn_rd_prev[27]),
        .I1(data_prev),
        .I2(trn_rd[59]),
        .O(p_1_in[27]));
  (* SOFT_HLUTNM = "soft_lutpair89" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[28]_i_1 
       (.I0(trn_rd_prev[28]),
        .I1(data_prev),
        .I2(trn_rd[60]),
        .O(p_1_in[28]));
  (* SOFT_HLUTNM = "soft_lutpair80" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[29]_i_1 
       (.I0(trn_rd_prev[29]),
        .I1(data_prev),
        .I2(trn_rd[61]),
        .O(p_1_in[29]));
  (* SOFT_HLUTNM = "soft_lutpair92" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[2]_i_1 
       (.I0(trn_rd_prev[2]),
        .I1(data_prev),
        .I2(trn_rd[34]),
        .O(p_1_in[2]));
  (* SOFT_HLUTNM = "soft_lutpair80" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[30]_i_1 
       (.I0(trn_rd_prev[30]),
        .I1(data_prev),
        .I2(trn_rd[62]),
        .O(p_1_in[30]));
  (* SOFT_HLUTNM = "soft_lutpair73" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[31]_i_1 
       (.I0(trn_rd_prev[31]),
        .I1(data_prev),
        .I2(trn_rd[63]),
        .O(p_1_in[31]));
  (* SOFT_HLUTNM = "soft_lutpair78" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[32]_i_1 
       (.I0(trn_rd_prev[32]),
        .I1(data_prev),
        .I2(trn_rd[0]),
        .O(p_1_in[32]));
  (* SOFT_HLUTNM = "soft_lutpair70" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[33]_i_1 
       (.I0(trn_rd_prev[33]),
        .I1(data_prev),
        .I2(trn_rd[1]),
        .O(p_1_in[33]));
  (* SOFT_HLUTNM = "soft_lutpair77" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[34]_i_1 
       (.I0(trn_rd_prev[34]),
        .I1(data_prev),
        .I2(trn_rd[2]),
        .O(p_1_in[34]));
  (* SOFT_HLUTNM = "soft_lutpair71" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[35]_i_1 
       (.I0(trn_rd_prev[35]),
        .I1(data_prev),
        .I2(trn_rd[3]),
        .O(p_1_in[35]));
  (* SOFT_HLUTNM = "soft_lutpair79" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[36]_i_1 
       (.I0(trn_rd_prev[36]),
        .I1(data_prev),
        .I2(trn_rd[4]),
        .O(p_1_in[36]));
  (* SOFT_HLUTNM = "soft_lutpair71" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[37]_i_1 
       (.I0(trn_rd_prev[37]),
        .I1(data_prev),
        .I2(trn_rd[5]),
        .O(p_1_in[37]));
  (* SOFT_HLUTNM = "soft_lutpair78" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[38]_i_1 
       (.I0(trn_rd_prev[38]),
        .I1(data_prev),
        .I2(trn_rd[6]),
        .O(p_1_in[38]));
  (* SOFT_HLUTNM = "soft_lutpair75" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[39]_i_1 
       (.I0(trn_rd_prev[39]),
        .I1(data_prev),
        .I2(trn_rd[7]),
        .O(p_1_in[39]));
  (* SOFT_HLUTNM = "soft_lutpair100" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[3]_i_1 
       (.I0(trn_rd_prev[3]),
        .I1(data_prev),
        .I2(trn_rd[35]),
        .O(p_1_in[3]));
  (* SOFT_HLUTNM = "soft_lutpair76" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[40]_i_1 
       (.I0(trn_rd_prev[40]),
        .I1(data_prev),
        .I2(trn_rd[8]),
        .O(p_1_in[40]));
  (* SOFT_HLUTNM = "soft_lutpair75" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[41]_i_1 
       (.I0(trn_rd_prev[41]),
        .I1(data_prev),
        .I2(trn_rd[9]),
        .O(p_1_in[41]));
  (* SOFT_HLUTNM = "soft_lutpair73" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[42]_i_1 
       (.I0(trn_rd_prev[42]),
        .I1(data_prev),
        .I2(trn_rd[10]),
        .O(p_1_in[42]));
  (* SOFT_HLUTNM = "soft_lutpair76" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[43]_i_1 
       (.I0(trn_rd_prev[43]),
        .I1(data_prev),
        .I2(trn_rd[11]),
        .O(p_1_in[43]));
  (* SOFT_HLUTNM = "soft_lutpair81" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[44]_i_1 
       (.I0(trn_rd_prev[44]),
        .I1(data_prev),
        .I2(trn_rd[12]),
        .O(p_1_in[44]));
  (* SOFT_HLUTNM = "soft_lutpair79" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[45]_i_1 
       (.I0(trn_rd_prev[45]),
        .I1(data_prev),
        .I2(trn_rd[13]),
        .O(p_1_in[45]));
  (* SOFT_HLUTNM = "soft_lutpair72" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[46]_i_1 
       (.I0(trn_rd_prev[46]),
        .I1(data_prev),
        .I2(trn_rd[14]),
        .O(p_1_in[46]));
  (* SOFT_HLUTNM = "soft_lutpair84" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[47]_i_1 
       (.I0(trn_rd_prev[47]),
        .I1(data_prev),
        .I2(trn_rd[15]),
        .O(p_1_in[47]));
  (* SOFT_HLUTNM = "soft_lutpair72" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[48]_i_1 
       (.I0(trn_rd_prev[48]),
        .I1(data_prev),
        .I2(trn_rd[16]),
        .O(p_1_in[48]));
  (* SOFT_HLUTNM = "soft_lutpair87" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[49]_i_1 
       (.I0(trn_rd_prev[49]),
        .I1(data_prev),
        .I2(trn_rd[17]),
        .O(p_1_in[49]));
  (* SOFT_HLUTNM = "soft_lutpair100" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[4]_i_1 
       (.I0(trn_rd_prev[4]),
        .I1(data_prev),
        .I2(trn_rd[36]),
        .O(p_1_in[4]));
  (* SOFT_HLUTNM = "soft_lutpair85" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[50]_i_1 
       (.I0(trn_rd_prev[50]),
        .I1(data_prev),
        .I2(trn_rd[18]),
        .O(p_1_in[50]));
  (* SOFT_HLUTNM = "soft_lutpair83" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[51]_i_1 
       (.I0(trn_rd_prev[51]),
        .I1(data_prev),
        .I2(trn_rd[19]),
        .O(p_1_in[51]));
  (* SOFT_HLUTNM = "soft_lutpair70" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[52]_i_1 
       (.I0(trn_rd_prev[52]),
        .I1(data_prev),
        .I2(trn_rd[20]),
        .O(p_1_in[52]));
  (* SOFT_HLUTNM = "soft_lutpair77" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[53]_i_1 
       (.I0(trn_rd_prev[53]),
        .I1(data_prev),
        .I2(trn_rd[21]),
        .O(p_1_in[53]));
  (* SOFT_HLUTNM = "soft_lutpair74" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[54]_i_1 
       (.I0(trn_rd_prev[54]),
        .I1(data_prev),
        .I2(trn_rd[22]),
        .O(p_1_in[54]));
  (* SOFT_HLUTNM = "soft_lutpair74" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[55]_i_1 
       (.I0(trn_rd_prev[55]),
        .I1(data_prev),
        .I2(trn_rd[23]),
        .O(p_1_in[55]));
  (* SOFT_HLUTNM = "soft_lutpair91" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[56]_i_1 
       (.I0(trn_rd_prev[56]),
        .I1(data_prev),
        .I2(trn_rd[24]),
        .O(p_1_in[56]));
  (* SOFT_HLUTNM = "soft_lutpair88" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[57]_i_1 
       (.I0(trn_rd_prev[57]),
        .I1(data_prev),
        .I2(trn_rd[25]),
        .O(p_1_in[57]));
  (* SOFT_HLUTNM = "soft_lutpair90" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[58]_i_1 
       (.I0(trn_rd_prev[58]),
        .I1(data_prev),
        .I2(trn_rd[26]),
        .O(p_1_in[58]));
  (* SOFT_HLUTNM = "soft_lutpair82" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[59]_i_1 
       (.I0(trn_rd_prev[59]),
        .I1(data_prev),
        .I2(trn_rd[27]),
        .O(p_1_in[59]));
  (* SOFT_HLUTNM = "soft_lutpair89" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[5]_i_1 
       (.I0(trn_rd_prev[5]),
        .I1(data_prev),
        .I2(trn_rd[37]),
        .O(p_1_in[5]));
  (* SOFT_HLUTNM = "soft_lutpair85" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[60]_i_1 
       (.I0(trn_rd_prev[60]),
        .I1(data_prev),
        .I2(trn_rd[28]),
        .O(p_1_in[60]));
  (* SOFT_HLUTNM = "soft_lutpair95" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[61]_i_1 
       (.I0(trn_rd_prev[61]),
        .I1(data_prev),
        .I2(trn_rd[29]),
        .O(p_1_in[61]));
  (* SOFT_HLUTNM = "soft_lutpair86" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[62]_i_1 
       (.I0(trn_rd_prev[62]),
        .I1(data_prev),
        .I2(trn_rd[30]),
        .O(p_1_in[62]));
  LUT2 #(
    .INIT(4'hB)) 
    \m_axis_rx_tdata[63]_i_1 
       (.I0(m_axis_rx_tready),
        .I1(m_axis_rx_tvalid_reg_0),
        .O(\m_axis_rx_tdata[63]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair99" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[63]_i_2 
       (.I0(trn_rd_prev[63]),
        .I1(data_prev),
        .I2(trn_rd[31]),
        .O(p_1_in[63]));
  (* SOFT_HLUTNM = "soft_lutpair87" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[6]_i_1 
       (.I0(trn_rd_prev[6]),
        .I1(data_prev),
        .I2(trn_rd[38]),
        .O(p_1_in[6]));
  (* SOFT_HLUTNM = "soft_lutpair97" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[7]_i_1 
       (.I0(trn_rd_prev[7]),
        .I1(data_prev),
        .I2(trn_rd[39]),
        .O(p_1_in[7]));
  (* SOFT_HLUTNM = "soft_lutpair96" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[8]_i_1 
       (.I0(trn_rd_prev[8]),
        .I1(data_prev),
        .I2(trn_rd[40]),
        .O(p_1_in[8]));
  (* SOFT_HLUTNM = "soft_lutpair93" *) 
  LUT3 #(
    .INIT(8'hB8)) 
    \m_axis_rx_tdata[9]_i_1 
       (.I0(trn_rd_prev[9]),
        .I1(data_prev),
        .I2(trn_rd[41]),
        .O(p_1_in[9]));
  FDRE \m_axis_rx_tdata_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[0]),
        .Q(Q[0]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[10] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[10]),
        .Q(Q[10]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[11] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[11]),
        .Q(Q[11]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[12] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[12]),
        .Q(Q[12]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[13] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[13]),
        .Q(Q[13]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[14] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[14]),
        .Q(Q[14]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[15] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[15]),
        .Q(Q[15]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[16] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[16]),
        .Q(Q[16]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[17] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[17]),
        .Q(Q[17]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[18] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[18]),
        .Q(Q[18]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[19] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[19]),
        .Q(Q[19]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[1]),
        .Q(Q[1]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[20] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[20]),
        .Q(Q[20]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[21] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[21]),
        .Q(Q[21]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[22] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[22]),
        .Q(Q[22]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[23] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[23]),
        .Q(Q[23]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[24] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[24]),
        .Q(Q[24]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[25] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[25]),
        .Q(Q[25]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[26] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[26]),
        .Q(Q[26]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[27] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[27]),
        .Q(Q[27]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[28] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[28]),
        .Q(Q[28]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[29] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[29]),
        .Q(Q[29]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[2]),
        .Q(Q[2]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[30] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[30]),
        .Q(Q[30]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[31] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[31]),
        .Q(Q[31]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[32] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[32]),
        .Q(Q[32]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[33] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[33]),
        .Q(Q[33]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[34] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[34]),
        .Q(Q[34]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[35] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[35]),
        .Q(Q[35]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[36] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[36]),
        .Q(Q[36]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[37] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[37]),
        .Q(Q[37]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[38] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[38]),
        .Q(Q[38]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[39] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[39]),
        .Q(Q[39]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[3]),
        .Q(Q[3]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[40] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[40]),
        .Q(Q[40]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[41] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[41]),
        .Q(Q[41]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[42] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[42]),
        .Q(Q[42]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[43] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[43]),
        .Q(Q[43]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[44] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[44]),
        .Q(Q[44]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[45] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[45]),
        .Q(Q[45]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[46] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[46]),
        .Q(Q[46]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[47] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[47]),
        .Q(Q[47]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[48] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[48]),
        .Q(Q[48]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[49] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[49]),
        .Q(Q[49]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[4]),
        .Q(Q[4]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[50] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[50]),
        .Q(Q[50]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[51] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[51]),
        .Q(Q[51]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[52] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[52]),
        .Q(Q[52]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[53] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[53]),
        .Q(Q[53]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[54] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[54]),
        .Q(Q[54]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[55] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[55]),
        .Q(Q[55]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[56] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[56]),
        .Q(Q[56]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[57] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[57]),
        .Q(Q[57]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[58] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[58]),
        .Q(Q[58]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[59] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[59]),
        .Q(Q[59]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[5]),
        .Q(Q[5]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[60] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[60]),
        .Q(Q[60]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[61] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[61]),
        .Q(Q[61]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[62] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[62]),
        .Q(Q[62]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[63] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[63]),
        .Q(Q[63]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[6]),
        .Q(Q[6]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[7]),
        .Q(Q[7]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[8] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[8]),
        .Q(Q[8]),
        .R(SR));
  FDRE \m_axis_rx_tdata_reg[9] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(p_1_in[9]),
        .Q(Q[9]),
        .R(SR));
  LUT5 #(
    .INIT(32'h000000E2)) 
    \m_axis_rx_tuser[0]_i_1 
       (.I0(trn_recrc_err),
        .I1(data_prev),
        .I2(trn_recrc_err_prev),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[0]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h0000000004F40404)) 
    \m_axis_rx_tuser[14]_i_1 
       (.I0(trn_rsrc_dsc),
        .I1(trn_rsof),
        .I2(data_prev),
        .I3(trn_rsrc_dsc_prev),
        .I4(trn_rsof_prev),
        .I5(\m_axis_rx_tuser[14]_i_2_n_0 ),
        .O(\m_axis_rx_tuser[14]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair67" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \m_axis_rx_tuser[14]_i_2 
       (.I0(SR),
        .I1(null_mux_sel),
        .O(\m_axis_rx_tuser[14]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair68" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \m_axis_rx_tuser[18]_i_1 
       (.I0(SR),
        .O(\m_axis_rx_tuser[18]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'h00E2)) 
    \m_axis_rx_tuser[19]_i_2 
       (.I0(trn_rrem),
        .I1(data_prev),
        .I2(trn_rrem_prev),
        .I3(null_mux_sel),
        .O(pcie_block_i_0));
  LUT5 #(
    .INIT(32'h000000B8)) 
    \m_axis_rx_tuser[1]_i_1 
       (.I0(trn_rerrfwd_prev),
        .I1(data_prev),
        .I2(trn_rerrfwd),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[1]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'hEF)) 
    \m_axis_rx_tuser[21]_i_1 
       (.I0(SR),
        .I1(m_axis_rx_tready),
        .I2(m_axis_rx_tvalid_reg_0),
        .O(\m_axis_rx_tuser[21]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair68" *) 
  LUT5 #(
    .INIT(32'h000000B8)) 
    \m_axis_rx_tuser[2]_i_1 
       (.I0(trn_rbar_hit_prev[0]),
        .I1(data_prev),
        .I2(trn_rbar_hit[0]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[2]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h000000E2)) 
    \m_axis_rx_tuser[3]_i_1 
       (.I0(trn_rbar_hit[1]),
        .I1(data_prev),
        .I2(trn_rbar_hit_prev[1]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[3]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h000000E2)) 
    \m_axis_rx_tuser[4]_i_1 
       (.I0(trn_rbar_hit[2]),
        .I1(data_prev),
        .I2(trn_rbar_hit_prev[2]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[4]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h000000B8)) 
    \m_axis_rx_tuser[5]_i_1 
       (.I0(trn_rbar_hit_prev[3]),
        .I1(data_prev),
        .I2(trn_rbar_hit[3]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[5]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h000000B8)) 
    \m_axis_rx_tuser[6]_i_1 
       (.I0(trn_rbar_hit_prev[4]),
        .I1(data_prev),
        .I2(trn_rbar_hit[4]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[6]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair67" *) 
  LUT5 #(
    .INIT(32'h000000E2)) 
    \m_axis_rx_tuser[7]_i_1 
       (.I0(trn_rbar_hit[5]),
        .I1(data_prev),
        .I2(trn_rbar_hit_prev[5]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[7]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h000000E2)) 
    \m_axis_rx_tuser[8]_i_1 
       (.I0(trn_rbar_hit[6]),
        .I1(data_prev),
        .I2(trn_rbar_hit_prev[6]),
        .I3(SR),
        .I4(null_mux_sel),
        .O(\m_axis_rx_tuser[8]_i_1_n_0 ));
  FDRE \m_axis_rx_tuser_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[0]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[0]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[14] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[14]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[9]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[18] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[18]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[10]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[19] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(D[0]),
        .Q(m_axis_rx_tuser[11]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[1]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[1]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[21] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(D[1]),
        .Q(m_axis_rx_tuser[12]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[2]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[2]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[3]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[3]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[4]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[4]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[5]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[5]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[6]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[6]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[7]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[7]),
        .R(1'b0));
  FDRE \m_axis_rx_tuser_reg[8] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tuser[21]_i_1_n_0 ),
        .D(\m_axis_rx_tuser[8]_i_1_n_0 ),
        .Q(m_axis_rx_tuser[8]),
        .R(1'b0));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFECE)) 
    m_axis_rx_tvalid_i_1
       (.I0(rsrc_rdy_filtered),
        .I1(null_mux_sel),
        .I2(data_prev),
        .I3(trn_rsrc_rdy_prev),
        .I4(reg_dsc_detect_reg_0),
        .I5(dsc_detect),
        .O(m_axis_rx_tvalid_i_1_n_0));
  FDRE m_axis_rx_tvalid_reg
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(m_axis_rx_tvalid_i_1_n_0),
        .Q(m_axis_rx_tvalid_reg_0),
        .R(SR));
  LUT6 #(
    .INIT(64'hABAAABAAABAABBBB)) 
    null_mux_sel_i_2
       (.I0(SR),
        .I1(null_mux_sel),
        .I2(m_axis_rx_tready),
        .I3(m_axis_rx_tvalid_reg_0),
        .I4(dsc_detect),
        .I5(reg_dsc_detect_reg_0),
        .O(user_reset_out_reg));
  FDRE null_mux_sel_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(null_mux_sel_reg_0),
        .Q(null_mux_sel),
        .R(1'b0));
  (* SOFT_HLUTNM = "soft_lutpair69" *) 
  LUT3 #(
    .INIT(8'hDC)) 
    reg_dsc_detect_i_1
       (.I0(null_mux_sel),
        .I1(dsc_detect),
        .I2(reg_dsc_detect_reg_0),
        .O(reg_dsc_detect_i_1_n_0));
  FDRE reg_dsc_detect_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(reg_dsc_detect_i_1_n_0),
        .Q(reg_dsc_detect_reg_0),
        .R(SR));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[10]_i_3 
       (.I0(Q[30]),
        .I1(Q[9]),
        .O(\reg_pkt_len_counter[10]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[10]_i_4 
       (.I0(Q[30]),
        .I1(Q[8]),
        .O(\reg_pkt_len_counter[10]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'hE)) 
    \reg_pkt_len_counter[3]_i_3 
       (.I0(Q[29]),
        .I1(Q[15]),
        .O(packet_overhead[1]));
  LUT2 #(
    .INIT(4'h9)) 
    \reg_pkt_len_counter[3]_i_4 
       (.I0(Q[15]),
        .I1(Q[29]),
        .O(packet_overhead[0]));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[3]_i_5 
       (.I0(Q[30]),
        .I1(Q[3]),
        .O(\reg_pkt_len_counter[3]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[3]_i_6 
       (.I0(Q[30]),
        .I1(Q[2]),
        .O(\reg_pkt_len_counter[3]_i_6_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[7]_i_3 
       (.I0(Q[30]),
        .I1(Q[7]),
        .O(\reg_pkt_len_counter[7]_i_3_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[7]_i_4 
       (.I0(Q[30]),
        .I1(Q[6]),
        .O(\reg_pkt_len_counter[7]_i_4_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[7]_i_5 
       (.I0(Q[30]),
        .I1(Q[5]),
        .O(\reg_pkt_len_counter[7]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_pkt_len_counter[7]_i_6 
       (.I0(Q[30]),
        .I1(Q[4]),
        .O(\reg_pkt_len_counter[7]_i_6_n_0 ));
  CARRY4 \reg_pkt_len_counter_reg[10]_i_2 
       (.CI(\reg_pkt_len_counter_reg[7]_i_2_n_0 ),
        .CO({\NLW_reg_pkt_len_counter_reg[10]_i_2_CO_UNCONNECTED [3],new_pkt_len[10],\NLW_reg_pkt_len_counter_reg[10]_i_2_CO_UNCONNECTED [1],\reg_pkt_len_counter_reg[10]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_reg_pkt_len_counter_reg[10]_i_2_O_UNCONNECTED [3:2],new_pkt_len[9:8]}),
        .S({1'b0,1'b1,\reg_pkt_len_counter[10]_i_3_n_0 ,\reg_pkt_len_counter[10]_i_4_n_0 }));
  CARRY4 \reg_pkt_len_counter_reg[3]_i_2 
       (.CI(1'b0),
        .CO({\reg_pkt_len_counter_reg[3]_i_2_n_0 ,\reg_pkt_len_counter_reg[3]_i_2_n_1 ,\reg_pkt_len_counter_reg[3]_i_2_n_2 ,\reg_pkt_len_counter_reg[3]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,packet_overhead}),
        .O(new_pkt_len[3:0]),
        .S({\reg_pkt_len_counter[3]_i_5_n_0 ,\reg_pkt_len_counter[3]_i_6_n_0 ,S}));
  CARRY4 \reg_pkt_len_counter_reg[7]_i_2 
       (.CI(\reg_pkt_len_counter_reg[3]_i_2_n_0 ),
        .CO({\reg_pkt_len_counter_reg[7]_i_2_n_0 ,\reg_pkt_len_counter_reg[7]_i_2_n_1 ,\reg_pkt_len_counter_reg[7]_i_2_n_2 ,\reg_pkt_len_counter_reg[7]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(new_pkt_len[7:4]),
        .S({\reg_pkt_len_counter[7]_i_3_n_0 ,\reg_pkt_len_counter[7]_i_4_n_0 ,\reg_pkt_len_counter[7]_i_5_n_0 ,\reg_pkt_len_counter[7]_i_6_n_0 }));
  LUT6 #(
    .INIT(64'h7F7F7F7070707F70)) 
    \reg_tkeep[7]_i_1 
       (.I0(trn_rdst_rdy_reg_0),
        .I1(\reg_tkeep_reg[7]_0 ),
        .I2(null_mux_sel),
        .I3(trn_rrem),
        .I4(data_prev),
        .I5(trn_rrem_prev),
        .O(reg_tkeep));
  FDSE \reg_tkeep_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(reg_tkeep),
        .Q(m_axis_rx_tkeep),
        .S(SR));
  LUT4 #(
    .INIT(16'h00E2)) 
    reg_tlast_i_2
       (.I0(trn_reof),
        .I1(data_prev),
        .I2(trn_reof_prev),
        .I3(null_mux_sel),
        .O(pcie_block_i));
  FDRE reg_tlast_reg
       (.C(pipe_userclk2_in),
        .CE(\m_axis_rx_tdata[63]_i_1_n_0 ),
        .D(reg_tlast_reg_0),
        .Q(m_axis_rx_tlast),
        .R(SR));
  FDRE trn_in_packet_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_in_packet_reg_0),
        .Q(trn_in_packet),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[0]),
        .Q(trn_rbar_hit_prev[0]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[1]),
        .Q(trn_rbar_hit_prev[1]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[2]),
        .Q(trn_rbar_hit_prev[2]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[3]),
        .Q(trn_rbar_hit_prev[3]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[4]),
        .Q(trn_rbar_hit_prev[4]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[5]),
        .Q(trn_rbar_hit_prev[5]),
        .R(SR));
  FDRE \trn_rbar_hit_prev_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rbar_hit[6]),
        .Q(trn_rbar_hit_prev[6]),
        .R(SR));
  FDRE \trn_rd_prev_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[32]),
        .Q(trn_rd_prev[0]),
        .R(SR));
  FDRE \trn_rd_prev_reg[10] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[42]),
        .Q(trn_rd_prev[10]),
        .R(SR));
  FDRE \trn_rd_prev_reg[11] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[43]),
        .Q(trn_rd_prev[11]),
        .R(SR));
  FDRE \trn_rd_prev_reg[12] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[44]),
        .Q(trn_rd_prev[12]),
        .R(SR));
  FDRE \trn_rd_prev_reg[13] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[45]),
        .Q(trn_rd_prev[13]),
        .R(SR));
  FDRE \trn_rd_prev_reg[14] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[46]),
        .Q(trn_rd_prev[14]),
        .R(SR));
  FDRE \trn_rd_prev_reg[15] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[47]),
        .Q(trn_rd_prev[15]),
        .R(SR));
  FDRE \trn_rd_prev_reg[16] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[48]),
        .Q(trn_rd_prev[16]),
        .R(SR));
  FDRE \trn_rd_prev_reg[17] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[49]),
        .Q(trn_rd_prev[17]),
        .R(SR));
  FDRE \trn_rd_prev_reg[18] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[50]),
        .Q(trn_rd_prev[18]),
        .R(SR));
  FDRE \trn_rd_prev_reg[19] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[51]),
        .Q(trn_rd_prev[19]),
        .R(SR));
  FDRE \trn_rd_prev_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[33]),
        .Q(trn_rd_prev[1]),
        .R(SR));
  FDRE \trn_rd_prev_reg[20] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[52]),
        .Q(trn_rd_prev[20]),
        .R(SR));
  FDRE \trn_rd_prev_reg[21] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[53]),
        .Q(trn_rd_prev[21]),
        .R(SR));
  FDRE \trn_rd_prev_reg[22] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[54]),
        .Q(trn_rd_prev[22]),
        .R(SR));
  FDRE \trn_rd_prev_reg[23] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[55]),
        .Q(trn_rd_prev[23]),
        .R(SR));
  FDRE \trn_rd_prev_reg[24] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[56]),
        .Q(trn_rd_prev[24]),
        .R(SR));
  FDRE \trn_rd_prev_reg[25] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[57]),
        .Q(trn_rd_prev[25]),
        .R(SR));
  FDRE \trn_rd_prev_reg[26] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[58]),
        .Q(trn_rd_prev[26]),
        .R(SR));
  FDRE \trn_rd_prev_reg[27] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[59]),
        .Q(trn_rd_prev[27]),
        .R(SR));
  FDRE \trn_rd_prev_reg[28] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[60]),
        .Q(trn_rd_prev[28]),
        .R(SR));
  FDRE \trn_rd_prev_reg[29] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[61]),
        .Q(trn_rd_prev[29]),
        .R(SR));
  FDRE \trn_rd_prev_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[34]),
        .Q(trn_rd_prev[2]),
        .R(SR));
  FDRE \trn_rd_prev_reg[30] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[62]),
        .Q(trn_rd_prev[30]),
        .R(SR));
  FDRE \trn_rd_prev_reg[31] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[63]),
        .Q(trn_rd_prev[31]),
        .R(SR));
  FDRE \trn_rd_prev_reg[32] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[0]),
        .Q(trn_rd_prev[32]),
        .R(SR));
  FDRE \trn_rd_prev_reg[33] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[1]),
        .Q(trn_rd_prev[33]),
        .R(SR));
  FDRE \trn_rd_prev_reg[34] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[2]),
        .Q(trn_rd_prev[34]),
        .R(SR));
  FDRE \trn_rd_prev_reg[35] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[3]),
        .Q(trn_rd_prev[35]),
        .R(SR));
  FDRE \trn_rd_prev_reg[36] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[4]),
        .Q(trn_rd_prev[36]),
        .R(SR));
  FDRE \trn_rd_prev_reg[37] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[5]),
        .Q(trn_rd_prev[37]),
        .R(SR));
  FDRE \trn_rd_prev_reg[38] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[6]),
        .Q(trn_rd_prev[38]),
        .R(SR));
  FDRE \trn_rd_prev_reg[39] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[7]),
        .Q(trn_rd_prev[39]),
        .R(SR));
  FDRE \trn_rd_prev_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[35]),
        .Q(trn_rd_prev[3]),
        .R(SR));
  FDRE \trn_rd_prev_reg[40] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[8]),
        .Q(trn_rd_prev[40]),
        .R(SR));
  FDRE \trn_rd_prev_reg[41] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[9]),
        .Q(trn_rd_prev[41]),
        .R(SR));
  FDRE \trn_rd_prev_reg[42] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[10]),
        .Q(trn_rd_prev[42]),
        .R(SR));
  FDRE \trn_rd_prev_reg[43] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[11]),
        .Q(trn_rd_prev[43]),
        .R(SR));
  FDRE \trn_rd_prev_reg[44] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[12]),
        .Q(trn_rd_prev[44]),
        .R(SR));
  FDRE \trn_rd_prev_reg[45] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[13]),
        .Q(trn_rd_prev[45]),
        .R(SR));
  FDRE \trn_rd_prev_reg[46] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[14]),
        .Q(trn_rd_prev[46]),
        .R(SR));
  FDRE \trn_rd_prev_reg[47] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[15]),
        .Q(trn_rd_prev[47]),
        .R(SR));
  FDRE \trn_rd_prev_reg[48] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[16]),
        .Q(trn_rd_prev[48]),
        .R(SR));
  FDRE \trn_rd_prev_reg[49] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[17]),
        .Q(trn_rd_prev[49]),
        .R(SR));
  FDRE \trn_rd_prev_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[36]),
        .Q(trn_rd_prev[4]),
        .R(SR));
  FDRE \trn_rd_prev_reg[50] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[18]),
        .Q(trn_rd_prev[50]),
        .R(SR));
  FDRE \trn_rd_prev_reg[51] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[19]),
        .Q(trn_rd_prev[51]),
        .R(SR));
  FDRE \trn_rd_prev_reg[52] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[20]),
        .Q(trn_rd_prev[52]),
        .R(SR));
  FDRE \trn_rd_prev_reg[53] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[21]),
        .Q(trn_rd_prev[53]),
        .R(SR));
  FDRE \trn_rd_prev_reg[54] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[22]),
        .Q(trn_rd_prev[54]),
        .R(SR));
  FDRE \trn_rd_prev_reg[55] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[23]),
        .Q(trn_rd_prev[55]),
        .R(SR));
  FDRE \trn_rd_prev_reg[56] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[24]),
        .Q(trn_rd_prev[56]),
        .R(SR));
  FDRE \trn_rd_prev_reg[57] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[25]),
        .Q(trn_rd_prev[57]),
        .R(SR));
  FDRE \trn_rd_prev_reg[58] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[26]),
        .Q(trn_rd_prev[58]),
        .R(SR));
  FDRE \trn_rd_prev_reg[59] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[27]),
        .Q(trn_rd_prev[59]),
        .R(SR));
  FDRE \trn_rd_prev_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[37]),
        .Q(trn_rd_prev[5]),
        .R(SR));
  FDRE \trn_rd_prev_reg[60] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[28]),
        .Q(trn_rd_prev[60]),
        .R(SR));
  FDRE \trn_rd_prev_reg[61] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[29]),
        .Q(trn_rd_prev[61]),
        .R(SR));
  FDRE \trn_rd_prev_reg[62] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[30]),
        .Q(trn_rd_prev[62]),
        .R(SR));
  FDRE \trn_rd_prev_reg[63] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[31]),
        .Q(trn_rd_prev[63]),
        .R(SR));
  FDRE \trn_rd_prev_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[38]),
        .Q(trn_rd_prev[6]),
        .R(SR));
  FDRE \trn_rd_prev_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[39]),
        .Q(trn_rd_prev[7]),
        .R(SR));
  FDRE \trn_rd_prev_reg[8] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[40]),
        .Q(trn_rd_prev[8]),
        .R(SR));
  FDRE \trn_rd_prev_reg[9] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rd[41]),
        .Q(trn_rd_prev[9]),
        .R(SR));
  LUT6 #(
    .INIT(64'h3030FF3050505050)) 
    trn_rdst_rdy_i_1
       (.I0(m_axis_rx_tvalid_reg_0),
        .I1(null_mux_sel),
        .I2(trn_rdst_rdy_i_2_n_0),
        .I3(trn_rdst_rdy_reg_0),
        .I4(trn_rdst_rdy_reg_1),
        .I5(m_axis_rx_tready),
        .O(trn_rdst_rdy_i_1_n_0));
  (* SOFT_HLUTNM = "soft_lutpair69" *) 
  LUT2 #(
    .INIT(4'h1)) 
    trn_rdst_rdy_i_2
       (.I0(reg_dsc_detect_reg_0),
        .I1(dsc_detect),
        .O(trn_rdst_rdy_i_2_n_0));
  FDRE trn_rdst_rdy_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_rdst_rdy_i_1_n_0),
        .Q(E),
        .R(SR));
  FDRE trn_recrc_err_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_recrc_err),
        .Q(trn_recrc_err_prev),
        .R(SR));
  FDRE trn_reof_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_reof),
        .Q(trn_reof_prev),
        .R(SR));
  FDRE trn_rerrfwd_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rerrfwd),
        .Q(trn_rerrfwd_prev),
        .R(SR));
  FDRE \trn_rrem_prev_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rrem),
        .Q(trn_rrem_prev),
        .R(SR));
  FDRE trn_rsof_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rsof),
        .Q(trn_rsof_prev),
        .R(SR));
  FDRE trn_rsrc_dsc_d_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_rsrc_dsc),
        .Q(trn_rsrc_dsc_d),
        .R(SR));
  FDRE trn_rsrc_dsc_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(trn_rsrc_dsc_prev0),
        .Q(trn_rsrc_dsc_prev),
        .R(SR));
  FDRE trn_rsrc_rdy_prev_reg
       (.C(pipe_userclk2_in),
        .CE(E),
        .D(rsrc_rdy_filtered),
        .Q(trn_rsrc_rdy_prev),
        .R(SR));
endmodule

module pcie_7x_bridge_axi_basic_top
   (E,
    trn_rsrc_dsc_d,
    m_axis_rx_tvalid_reg,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
    reg_tcfg_gnt,
    tready_thrtl_reg,
    trn_teof,
    trn_tsrc_rdy,
    trn_trem,
    trn_in_packet,
    reg_dsc_detect,
    ppm_L1_thrtl,
    lnk_up_thrtl,
    m_axis_rx_tuser,
    ppm_L1_trig,
    cfg_pm_turnoff_ok_n,
    trn_tcfg_gnt,
    trn_tsof,
    Q,
    \throttle_ctl_pipeline.reg_tdata_reg[63] ,
    \throttle_ctl_pipeline.reg_tuser_reg[3] ,
    SR,
    pipe_userclk2_in,
    trn_rrem,
    trn_rsrc_dsc,
    rsrc_rdy_filtered,
    trn_reof,
    trn_rsrc_dsc_prev0,
    trn_rsof,
    trn_recrc_err,
    trn_rerrfwd,
    tx_cfg_gnt,
    trn_tcfg_req,
    trn_tdst_rdy,
    tbuf_av_min_trig,
    cfg_turnoff_ok,
    s_axis_tx_tlast,
    s_axis_tx_tvalid,
    s_axis_tx_tkeep,
    trn_in_packet_reg,
    ppm_L1_thrtl_reg,
    lnk_up_thrtl_reg,
    m_axis_rx_tready,
    dsc_detect,
    out,
    tcfg_req_trig,
    tready_thrtl_i_5,
    cfg_pcie_link_state,
    s_axis_tx_tdata,
    s_axis_tx_tuser,
    trn_tbuf_av,
    trn_rd,
    trn_rbar_hit,
    cfg_to_turnoff);
  output [0:0]E;
  output trn_rsrc_dsc_d;
  output m_axis_rx_tvalid_reg;
  output [0:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output reg_tcfg_gnt;
  output tready_thrtl_reg;
  output trn_teof;
  output trn_tsrc_rdy;
  output [0:0]trn_trem;
  output trn_in_packet;
  output reg_dsc_detect;
  output ppm_L1_thrtl;
  output lnk_up_thrtl;
  output [12:0]m_axis_rx_tuser;
  output ppm_L1_trig;
  output cfg_pm_turnoff_ok_n;
  output trn_tcfg_gnt;
  output trn_tsof;
  output [63:0]Q;
  output [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63] ;
  output [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3] ;
  input [0:0]SR;
  input pipe_userclk2_in;
  input [0:0]trn_rrem;
  input trn_rsrc_dsc;
  input rsrc_rdy_filtered;
  input trn_reof;
  input trn_rsrc_dsc_prev0;
  input trn_rsof;
  input trn_recrc_err;
  input trn_rerrfwd;
  input tx_cfg_gnt;
  input trn_tcfg_req;
  input trn_tdst_rdy;
  input tbuf_av_min_trig;
  input cfg_turnoff_ok;
  input s_axis_tx_tlast;
  input s_axis_tx_tvalid;
  input [0:0]s_axis_tx_tkeep;
  input trn_in_packet_reg;
  input ppm_L1_thrtl_reg;
  input lnk_up_thrtl_reg;
  input m_axis_rx_tready;
  input dsc_detect;
  input out;
  input tcfg_req_trig;
  input tready_thrtl_i_5;
  input [2:0]cfg_pcie_link_state;
  input [63:0]s_axis_tx_tdata;
  input [3:0]s_axis_tx_tuser;
  input [5:0]trn_tbuf_av;
  input [63:0]trn_rd;
  input [6:0]trn_rbar_hit;
  input cfg_to_turnoff;

  wire [0:0]E;
  wire [63:0]Q;
  wire [0:0]SR;
  wire [2:0]cfg_pcie_link_state;
  wire cfg_pm_turnoff_ok_n;
  wire cfg_to_turnoff;
  wire cfg_turnoff_ok;
  wire dsc_detect;
  wire lnk_up_thrtl;
  wire lnk_up_thrtl_reg;
  wire [0:0]m_axis_rx_tkeep;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [12:0]m_axis_rx_tuser;
  wire m_axis_rx_tvalid_reg;
  wire out;
  wire pipe_userclk2_in;
  wire ppm_L1_thrtl;
  wire ppm_L1_thrtl_reg;
  wire ppm_L1_trig;
  wire reg_dsc_detect;
  wire reg_tcfg_gnt;
  wire rsrc_rdy_filtered;
  wire [63:0]s_axis_tx_tdata;
  wire [0:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire tbuf_av_min_trig;
  wire tcfg_req_trig;
  wire [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63] ;
  wire [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3] ;
  wire tready_thrtl_i_5;
  wire tready_thrtl_reg;
  wire trn_in_packet;
  wire trn_in_packet_reg;
  wire [6:0]trn_rbar_hit;
  wire [63:0]trn_rd;
  wire trn_recrc_err;
  wire trn_reof;
  wire trn_rerrfwd;
  wire [0:0]trn_rrem;
  wire trn_rsof;
  wire trn_rsrc_dsc;
  wire trn_rsrc_dsc_d;
  wire trn_rsrc_dsc_prev0;
  wire [5:0]trn_tbuf_av;
  wire trn_tcfg_gnt;
  wire trn_tcfg_req;
  wire trn_tdst_rdy;
  wire trn_teof;
  wire [0:0]trn_trem;
  wire trn_tsof;
  wire trn_tsrc_rdy;
  wire tx_cfg_gnt;

  pcie_7x_bridge_axi_basic_rx rx_inst
       (.E(E),
        .Q(Q),
        .SR(SR),
        .dsc_detect(dsc_detect),
        .m_axis_rx_tkeep(m_axis_rx_tkeep),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(m_axis_rx_tuser),
        .m_axis_rx_tvalid_reg(m_axis_rx_tvalid_reg),
        .pipe_userclk2_in(pipe_userclk2_in),
        .reg_dsc_detect_reg(reg_dsc_detect),
        .rsrc_rdy_filtered(rsrc_rdy_filtered),
        .trn_in_packet(trn_in_packet),
        .trn_in_packet_reg(trn_in_packet_reg),
        .trn_rbar_hit(trn_rbar_hit),
        .trn_rd(trn_rd),
        .trn_recrc_err(trn_recrc_err),
        .trn_reof(trn_reof),
        .trn_rerrfwd(trn_rerrfwd),
        .trn_rrem(trn_rrem),
        .trn_rsof(trn_rsof),
        .trn_rsrc_dsc(trn_rsrc_dsc),
        .trn_rsrc_dsc_d(trn_rsrc_dsc_d),
        .trn_rsrc_dsc_prev0(trn_rsrc_dsc_prev0));
  pcie_7x_bridge_axi_basic_tx tx_inst
       (.SR(SR),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pm_turnoff_ok_n(cfg_pm_turnoff_ok_n),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .lnk_up_thrtl(lnk_up_thrtl),
        .lnk_up_thrtl_reg(lnk_up_thrtl_reg),
        .out(out),
        .pipe_userclk2_in(pipe_userclk2_in),
        .ppm_L1_thrtl(ppm_L1_thrtl),
        .ppm_L1_thrtl_reg(ppm_L1_thrtl_reg),
        .ppm_L1_trig(ppm_L1_trig),
        .reg_tcfg_gnt(reg_tcfg_gnt),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep(s_axis_tx_tkeep),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .tbuf_av_min_trig(tbuf_av_min_trig),
        .tcfg_req_trig(tcfg_req_trig),
        .\throttle_ctl_pipeline.reg_tdata_reg[63] (\throttle_ctl_pipeline.reg_tdata_reg[63] ),
        .\throttle_ctl_pipeline.reg_tuser_reg[3] (\throttle_ctl_pipeline.reg_tuser_reg[3] ),
        .tready_thrtl_i_5(tready_thrtl_i_5),
        .tready_thrtl_reg(tready_thrtl_reg),
        .trn_tbuf_av(trn_tbuf_av),
        .trn_tcfg_gnt(trn_tcfg_gnt),
        .trn_tcfg_req(trn_tcfg_req),
        .trn_tdst_rdy(trn_tdst_rdy),
        .trn_teof(trn_teof),
        .trn_trem(trn_trem),
        .trn_tsof(trn_tsof),
        .trn_tsrc_rdy(trn_tsrc_rdy),
        .tx_cfg_gnt(tx_cfg_gnt));
endmodule

module pcie_7x_bridge_axi_basic_tx
   (reg_tcfg_gnt,
    tready_thrtl_reg,
    trn_teof,
    trn_tsrc_rdy,
    trn_trem,
    ppm_L1_thrtl,
    lnk_up_thrtl,
    ppm_L1_trig,
    cfg_pm_turnoff_ok_n,
    trn_tcfg_gnt,
    trn_tsof,
    \throttle_ctl_pipeline.reg_tdata_reg[63] ,
    \throttle_ctl_pipeline.reg_tuser_reg[3] ,
    SR,
    tx_cfg_gnt,
    pipe_userclk2_in,
    trn_tcfg_req,
    trn_tdst_rdy,
    tbuf_av_min_trig,
    cfg_turnoff_ok,
    s_axis_tx_tlast,
    s_axis_tx_tvalid,
    s_axis_tx_tkeep,
    ppm_L1_thrtl_reg,
    lnk_up_thrtl_reg,
    out,
    tcfg_req_trig,
    tready_thrtl_i_5,
    cfg_pcie_link_state,
    s_axis_tx_tdata,
    s_axis_tx_tuser,
    trn_tbuf_av,
    cfg_to_turnoff);
  output reg_tcfg_gnt;
  output tready_thrtl_reg;
  output trn_teof;
  output trn_tsrc_rdy;
  output [0:0]trn_trem;
  output ppm_L1_thrtl;
  output lnk_up_thrtl;
  output ppm_L1_trig;
  output cfg_pm_turnoff_ok_n;
  output trn_tcfg_gnt;
  output trn_tsof;
  output [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63] ;
  output [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3] ;
  input [0:0]SR;
  input tx_cfg_gnt;
  input pipe_userclk2_in;
  input trn_tcfg_req;
  input trn_tdst_rdy;
  input tbuf_av_min_trig;
  input cfg_turnoff_ok;
  input s_axis_tx_tlast;
  input s_axis_tx_tvalid;
  input [0:0]s_axis_tx_tkeep;
  input ppm_L1_thrtl_reg;
  input lnk_up_thrtl_reg;
  input out;
  input tcfg_req_trig;
  input tready_thrtl_i_5;
  input [2:0]cfg_pcie_link_state;
  input [63:0]s_axis_tx_tdata;
  input [3:0]s_axis_tx_tuser;
  input [5:0]trn_tbuf_av;
  input cfg_to_turnoff;

  wire [0:0]SR;
  wire axi_in_packet;
  wire [2:0]cfg_pcie_link_state;
  wire cfg_pm_turnoff_ok_n;
  wire cfg_to_turnoff;
  wire cfg_turnoff_ok;
  wire lnk_up_thrtl;
  wire lnk_up_thrtl_reg;
  wire out;
  wire pipe_userclk2_in;
  wire ppm_L1_thrtl;
  wire ppm_L1_thrtl_reg;
  wire ppm_L1_trig;
  wire reg_disable_trn;
  wire reg_tcfg_gnt;
  wire reg_tsrc_rdy0;
  wire [63:0]s_axis_tx_tdata;
  wire [0:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire tbuf_av_min_trig;
  wire tcfg_req_trig;
  wire [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63] ;
  wire [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3] ;
  wire \thrtl_ctl_enabled.tx_thrl_ctl_inst_n_4 ;
  wire tready_thrtl_i_5;
  wire tready_thrtl_reg;
  wire [5:0]trn_tbuf_av;
  wire trn_tcfg_gnt;
  wire trn_tcfg_req;
  wire trn_tdst_rdy;
  wire trn_teof;
  wire [0:0]trn_trem;
  wire trn_tsof;
  wire trn_tsrc_rdy;
  wire tx_cfg_gnt;

  pcie_7x_bridge_axi_basic_tx_thrtl_ctl \thrtl_ctl_enabled.tx_thrl_ctl_inst 
       (.SR(SR),
        .axi_in_packet(axi_in_packet),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pm_turnoff_ok_n(cfg_pm_turnoff_ok_n),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .lnk_up_thrtl(lnk_up_thrtl),
        .lnk_up_thrtl_reg_0(lnk_up_thrtl_reg),
        .out(out),
        .pipe_userclk2_in(pipe_userclk2_in),
        .ppm_L1_thrtl(ppm_L1_thrtl),
        .ppm_L1_thrtl_reg_0(ppm_L1_thrtl_reg),
        .ppm_L1_trig(ppm_L1_trig),
        .reg_disable_trn(reg_disable_trn),
        .reg_tcfg_gnt(reg_tcfg_gnt),
        .reg_tsrc_rdy0(reg_tsrc_rdy0),
        .s_axis_tx_tdata({s_axis_tx_tdata[30:29],s_axis_tx_tdata[15],s_axis_tx_tdata[0]}),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tlast_0(\thrtl_ctl_enabled.tx_thrl_ctl_inst_n_4 ),
        .s_axis_tx_tuser(s_axis_tx_tuser[0]),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .tbuf_av_min_trig(tbuf_av_min_trig),
        .tcfg_req_trig(tcfg_req_trig),
        .tready_thrtl_i_5_0(tready_thrtl_i_5),
        .tready_thrtl_reg_0(tready_thrtl_reg),
        .trn_tbuf_av(trn_tbuf_av),
        .trn_tcfg_gnt(trn_tcfg_gnt),
        .trn_tcfg_req(trn_tcfg_req),
        .trn_tdst_rdy(trn_tdst_rdy),
        .tx_cfg_gnt(tx_cfg_gnt));
  pcie_7x_bridge_axi_basic_tx_pipeline tx_pipeline_inst
       (.SR(SR),
        .axi_in_packet(axi_in_packet),
        .axi_in_packet_reg_0(\thrtl_ctl_enabled.tx_thrl_ctl_inst_n_4 ),
        .out(out),
        .pipe_userclk2_in(pipe_userclk2_in),
        .reg_disable_trn(reg_disable_trn),
        .reg_tsrc_rdy0(reg_tsrc_rdy0),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep(s_axis_tx_tkeep),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .\throttle_ctl_pipeline.reg_tdata_reg[63]_0 (\throttle_ctl_pipeline.reg_tdata_reg[63] ),
        .\throttle_ctl_pipeline.reg_tuser_reg[3]_0 (\throttle_ctl_pipeline.reg_tuser_reg[3] ),
        .\thrtl_ctl_trn_flush.reg_disable_trn_reg_0 (tready_thrtl_reg),
        .trn_tdst_rdy(trn_tdst_rdy),
        .trn_teof(trn_teof),
        .trn_trem(trn_trem),
        .trn_tsof(trn_tsof),
        .trn_tsrc_rdy(trn_tsrc_rdy));
endmodule

module pcie_7x_bridge_axi_basic_tx_pipeline
   (trn_teof,
    trn_tsrc_rdy,
    trn_trem,
    axi_in_packet,
    reg_disable_trn,
    trn_tsof,
    \throttle_ctl_pipeline.reg_tdata_reg[63]_0 ,
    \throttle_ctl_pipeline.reg_tuser_reg[3]_0 ,
    SR,
    s_axis_tx_tlast,
    pipe_userclk2_in,
    reg_tsrc_rdy0,
    s_axis_tx_tvalid,
    s_axis_tx_tkeep,
    axi_in_packet_reg_0,
    out,
    \thrtl_ctl_trn_flush.reg_disable_trn_reg_0 ,
    trn_tdst_rdy,
    s_axis_tx_tdata,
    s_axis_tx_tuser);
  output trn_teof;
  output trn_tsrc_rdy;
  output [0:0]trn_trem;
  output axi_in_packet;
  output reg_disable_trn;
  output trn_tsof;
  output [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63]_0 ;
  output [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3]_0 ;
  input [0:0]SR;
  input s_axis_tx_tlast;
  input pipe_userclk2_in;
  input reg_tsrc_rdy0;
  input s_axis_tx_tvalid;
  input [0:0]s_axis_tx_tkeep;
  input axi_in_packet_reg_0;
  input out;
  input \thrtl_ctl_trn_flush.reg_disable_trn_reg_0 ;
  input trn_tdst_rdy;
  input [63:0]s_axis_tx_tdata;
  input [3:0]s_axis_tx_tuser;

  wire [0:0]SR;
  wire axi_in_packet;
  wire axi_in_packet_reg_0;
  wire out;
  wire pipe_userclk2_in;
  wire reg_disable_trn;
  wire reg_tsrc_rdy0;
  wire reg_tvalid;
  wire [63:0]s_axis_tx_tdata;
  wire [0:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire [63:0]\throttle_ctl_pipeline.reg_tdata_reg[63]_0 ;
  wire [3:0]\throttle_ctl_pipeline.reg_tuser_reg[3]_0 ;
  wire \thrtl_ctl_trn_flush.reg_disable_trn_i_1_n_0 ;
  wire \thrtl_ctl_trn_flush.reg_disable_trn_reg_0 ;
  wire trn_in_packet;
  wire trn_in_packet_i_1__0_n_0;
  wire trn_tdst_rdy;
  wire trn_teof;
  wire [0:0]trn_trem;
  wire trn_tsof;
  wire trn_tsrc_rdy;

  FDRE axi_in_packet_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(axi_in_packet_reg_0),
        .Q(axi_in_packet),
        .R(SR));
  LUT2 #(
    .INIT(4'h2)) 
    pcie_block_i_i_31
       (.I0(reg_tvalid),
        .I1(trn_in_packet),
        .O(trn_tsof));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[0]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [0]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[10] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[10]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [10]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[11] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[11]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [11]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[12] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[12]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [12]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[13] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[13]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [13]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[14] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[14]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [14]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[15] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[15]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [15]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[16] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[16]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [16]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[17] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[17]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [17]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[18] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[18]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [18]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[19] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[19]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [19]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[1]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [1]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[20] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[20]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [20]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[21] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[21]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [21]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[22] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[22]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [22]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[23] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[23]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [23]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[24] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[24]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [24]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[25] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[25]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [25]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[26] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[26]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [26]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[27] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[27]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [27]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[28] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[28]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [28]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[29] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[29]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [29]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[2]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [2]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[30] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[30]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [30]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[31] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[31]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [31]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[32] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[32]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [32]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[33] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[33]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [33]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[34] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[34]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [34]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[35] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[35]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [35]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[36] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[36]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [36]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[37] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[37]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [37]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[38] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[38]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [38]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[39] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[39]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [39]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[3]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [3]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[40] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[40]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [40]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[41] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[41]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [41]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[42] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[42]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [42]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[43] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[43]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [43]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[44] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[44]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [44]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[45] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[45]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [45]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[46] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[46]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [46]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[47] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[47]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [47]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[48] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[48]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [48]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[49] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[49]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [49]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[4]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [4]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[50] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[50]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [50]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[51] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[51]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [51]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[52] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[52]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [52]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[53] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[53]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [53]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[54] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[54]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [54]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[55] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[55]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [55]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[56] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[56]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [56]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[57] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[57]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [57]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[58] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[58]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [58]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[59] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[59]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [59]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[5]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [5]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[60] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[60]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [60]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[61] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[61]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [61]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[62] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[62]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [62]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[63] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[63]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [63]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[6]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [6]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[7]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [7]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[8] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[8]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [8]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tdata_reg[9] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tdata[9]),
        .Q(\throttle_ctl_pipeline.reg_tdata_reg[63]_0 [9]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tkeep_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tkeep),
        .Q(trn_trem),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tlast_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tlast),
        .Q(trn_teof),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tsrc_rdy_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(reg_tsrc_rdy0),
        .Q(trn_tsrc_rdy),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tuser_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tuser[0]),
        .Q(\throttle_ctl_pipeline.reg_tuser_reg[3]_0 [0]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tuser_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tuser[1]),
        .Q(\throttle_ctl_pipeline.reg_tuser_reg[3]_0 [1]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tuser_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tuser[2]),
        .Q(\throttle_ctl_pipeline.reg_tuser_reg[3]_0 [2]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tuser_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tuser[3]),
        .Q(\throttle_ctl_pipeline.reg_tuser_reg[3]_0 [3]),
        .R(SR));
  FDRE \throttle_ctl_pipeline.reg_tvalid_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(s_axis_tx_tvalid),
        .Q(reg_tvalid),
        .R(SR));
  LUT6 #(
    .INIT(64'h0FFFFFFF04444444)) 
    \thrtl_ctl_trn_flush.reg_disable_trn_i_1 
       (.I0(out),
        .I1(axi_in_packet),
        .I2(\thrtl_ctl_trn_flush.reg_disable_trn_reg_0 ),
        .I3(s_axis_tx_tvalid),
        .I4(s_axis_tx_tlast),
        .I5(reg_disable_trn),
        .O(\thrtl_ctl_trn_flush.reg_disable_trn_i_1_n_0 ));
  FDRE \thrtl_ctl_trn_flush.reg_disable_trn_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\thrtl_ctl_trn_flush.reg_disable_trn_i_1_n_0 ),
        .Q(reg_disable_trn),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000F088F000F000)) 
    trn_in_packet_i_1__0
       (.I0(trn_tdst_rdy),
        .I1(reg_tvalid),
        .I2(out),
        .I3(trn_in_packet),
        .I4(trn_teof),
        .I5(trn_tsrc_rdy),
        .O(trn_in_packet_i_1__0_n_0));
  FDRE trn_in_packet_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_in_packet_i_1__0_n_0),
        .Q(trn_in_packet),
        .R(SR));
endmodule

module pcie_7x_bridge_axi_basic_tx_thrtl_ctl
   (reg_tcfg_gnt,
    tready_thrtl_reg_0,
    ppm_L1_thrtl,
    lnk_up_thrtl,
    s_axis_tx_tlast_0,
    ppm_L1_trig,
    cfg_pm_turnoff_ok_n,
    trn_tcfg_gnt,
    reg_tsrc_rdy0,
    SR,
    tx_cfg_gnt,
    pipe_userclk2_in,
    trn_tcfg_req,
    trn_tdst_rdy,
    tbuf_av_min_trig,
    cfg_turnoff_ok,
    ppm_L1_thrtl_reg_0,
    lnk_up_thrtl_reg_0,
    s_axis_tx_tlast,
    s_axis_tx_tvalid,
    axi_in_packet,
    out,
    tcfg_req_trig,
    tready_thrtl_i_5_0,
    cfg_pcie_link_state,
    s_axis_tx_tdata,
    s_axis_tx_tuser,
    reg_disable_trn,
    trn_tbuf_av,
    cfg_to_turnoff);
  output reg_tcfg_gnt;
  output tready_thrtl_reg_0;
  output ppm_L1_thrtl;
  output lnk_up_thrtl;
  output s_axis_tx_tlast_0;
  output ppm_L1_trig;
  output cfg_pm_turnoff_ok_n;
  output trn_tcfg_gnt;
  output reg_tsrc_rdy0;
  input [0:0]SR;
  input tx_cfg_gnt;
  input pipe_userclk2_in;
  input trn_tcfg_req;
  input trn_tdst_rdy;
  input tbuf_av_min_trig;
  input cfg_turnoff_ok;
  input ppm_L1_thrtl_reg_0;
  input lnk_up_thrtl_reg_0;
  input s_axis_tx_tlast;
  input s_axis_tx_tvalid;
  input axi_in_packet;
  input out;
  input tcfg_req_trig;
  input tready_thrtl_i_5_0;
  input [2:0]cfg_pcie_link_state;
  input [3:0]s_axis_tx_tdata;
  input [0:0]s_axis_tx_tuser;
  input reg_disable_trn;
  input [5:0]trn_tbuf_av;
  input cfg_to_turnoff;

  wire \L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ;
  wire \L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff_i_1_n_0 ;
  wire [0:0]SR;
  wire axi_in_packet;
  wire [2:0]cfg_pcie_link_state;
  wire [2:0]cfg_pcie_link_state_d;
  wire cfg_pm_turnoff_ok_n;
  wire cfg_to_turnoff;
  wire cfg_turnoff_ok;
  wire cfg_turnoff_ok_pending;
  wire cfg_turnoff_ok_pending_i_1_n_0;
  wire cur_state;
  wire cur_state_i_2_n_0;
  wire \ecrc_pause_enabled.reg_tx_ecrc_pkt ;
  wire \ecrc_pause_enabled.reg_tx_ecrc_pkt021_out ;
  wire \ecrc_pause_enabled.reg_tx_ecrc_pkt_i_1_n_0 ;
  wire lnk_up_thrtl;
  wire lnk_up_thrtl_reg_0;
  wire next_state;
  wire out;
  wire p_2_in;
  wire pcie_block_i_i_38_n_0;
  wire pipe_userclk2_in;
  wire ppm_L1_thrtl;
  wire ppm_L1_thrtl_reg_0;
  wire ppm_L1_trig;
  wire ppm_L23_thrtl;
  wire ppm_L23_thrtl_i_1_n_0;
  wire ppm_L23_trig;
  wire reg_axi_in_pkt;
  wire reg_axi_in_pkt_i_1_n_0;
  wire reg_disable_trn;
  wire reg_tcfg_gnt;
  wire reg_tsrc_rdy0;
  wire reg_turnoff_ok;
  wire [3:0]s_axis_tx_tdata;
  wire s_axis_tx_tlast;
  wire s_axis_tx_tlast_0;
  wire [0:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire [5:0]tbuf_av_d;
  wire tbuf_av_gap_thrtl;
  wire tbuf_av_gap_thrtl_i_1_n_0;
  wire tbuf_av_gap_trig;
  wire tbuf_av_min_thrtl;
  wire tbuf_av_min_trig;
  wire \tbuf_gap_cnt[0]_i_1_n_0 ;
  wire \tbuf_gap_cnt_reg_n_0_[0] ;
  wire tcfg_gnt_pending;
  wire tcfg_gnt_pending_i_1_n_0;
  wire [1:0]tcfg_req_cnt;
  wire \tcfg_req_cnt[0]_i_1_n_0 ;
  wire \tcfg_req_cnt[1]_i_1_n_0 ;
  wire tcfg_req_thrtl;
  wire tcfg_req_thrtl_i_1_n_0;
  wire tcfg_req_trig;
  wire tready_thrtl0;
  wire tready_thrtl_i_10_n_0;
  wire tready_thrtl_i_12_n_0;
  wire tready_thrtl_i_2_n_0;
  wire tready_thrtl_i_3_n_0;
  wire tready_thrtl_i_4_n_0;
  wire tready_thrtl_i_5_0;
  wire tready_thrtl_i_6_n_0;
  wire tready_thrtl_i_7_n_0;
  wire tready_thrtl_reg_0;
  wire [5:0]trn_tbuf_av;
  wire trn_tcfg_gnt;
  wire trn_tcfg_req;
  wire trn_tcfg_req_d;
  wire trn_tdst_rdy;
  wire trn_tdst_rdy_d;
  wire tx_cfg_gnt;

  FDRE \L23_thrtl_ep.reg_turnoff_ok_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(cfg_turnoff_ok),
        .Q(reg_turnoff_ok),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair107" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff_i_1 
       (.I0(cfg_to_turnoff),
        .I1(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ),
        .O(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff_i_1_n_0 ));
  FDRE \L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff_i_1_n_0 ),
        .Q(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ),
        .R(SR));
  LUT4 #(
    .INIT(16'h7F40)) 
    axi_in_packet_i_1
       (.I0(s_axis_tx_tlast),
        .I1(s_axis_tx_tvalid),
        .I2(tready_thrtl_reg_0),
        .I3(axi_in_packet),
        .O(s_axis_tx_tlast_0));
  FDRE \cfg_pcie_link_state_d_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(cfg_pcie_link_state[0]),
        .Q(cfg_pcie_link_state_d[0]),
        .R(SR));
  FDRE \cfg_pcie_link_state_d_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(cfg_pcie_link_state[1]),
        .Q(cfg_pcie_link_state_d[1]),
        .R(SR));
  FDRE \cfg_pcie_link_state_d_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(cfg_pcie_link_state[2]),
        .Q(cfg_pcie_link_state_d[2]),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair104" *) 
  LUT5 #(
    .INIT(32'h75553000)) 
    cfg_turnoff_ok_pending_i_1
       (.I0(cfg_pm_turnoff_ok_n),
        .I1(ppm_L23_thrtl),
        .I2(reg_turnoff_ok),
        .I3(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ),
        .I4(cfg_turnoff_ok_pending),
        .O(cfg_turnoff_ok_pending_i_1_n_0));
  FDRE cfg_turnoff_ok_pending_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(cfg_turnoff_ok_pending_i_1_n_0),
        .Q(cfg_turnoff_ok_pending),
        .R(SR));
  LUT6 #(
    .INIT(64'h5455445554555555)) 
    cur_state_i_1__0
       (.I0(cur_state_i_2_n_0),
        .I1(cur_state),
        .I2(s_axis_tx_tlast),
        .I3(tready_thrtl_reg_0),
        .I4(s_axis_tx_tvalid),
        .I5(reg_axi_in_pkt),
        .O(next_state));
  LUT6 #(
    .INIT(64'h0000000000000001)) 
    cur_state_i_2
       (.I0(ppm_L1_thrtl),
        .I1(lnk_up_thrtl),
        .I2(tcfg_req_thrtl),
        .I3(ppm_L23_thrtl),
        .I4(tbuf_av_gap_thrtl),
        .I5(tbuf_av_min_thrtl),
        .O(cur_state_i_2_n_0));
  FDSE cur_state_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(next_state),
        .Q(cur_state),
        .S(SR));
  LUT5 #(
    .INIT(32'hBFFFAAAA)) 
    \ecrc_pause_enabled.reg_tx_ecrc_pkt_i_1 
       (.I0(\ecrc_pause_enabled.reg_tx_ecrc_pkt021_out ),
        .I1(tready_thrtl_reg_0),
        .I2(s_axis_tx_tvalid),
        .I3(s_axis_tx_tlast),
        .I4(\ecrc_pause_enabled.reg_tx_ecrc_pkt ),
        .O(\ecrc_pause_enabled.reg_tx_ecrc_pkt_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair105" *) 
  LUT5 #(
    .INIT(32'h00001444)) 
    \ecrc_pause_enabled.reg_tx_ecrc_pkt_i_2 
       (.I0(tready_thrtl_i_7_n_0),
        .I1(s_axis_tx_tdata[2]),
        .I2(s_axis_tx_tdata[3]),
        .I3(s_axis_tx_tdata[0]),
        .I4(s_axis_tx_tlast),
        .O(\ecrc_pause_enabled.reg_tx_ecrc_pkt021_out ));
  FDRE \ecrc_pause_enabled.reg_tx_ecrc_pkt_reg 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\ecrc_pause_enabled.reg_tx_ecrc_pkt_i_1_n_0 ),
        .Q(\ecrc_pause_enabled.reg_tx_ecrc_pkt ),
        .R(SR));
  FDSE lnk_up_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(lnk_up_thrtl_reg_0),
        .Q(lnk_up_thrtl),
        .S(SR));
  LUT6 #(
    .INIT(64'h20202020A0AFA0A0)) 
    pcie_block_i_i_26
       (.I0(cfg_turnoff_ok_pending),
        .I1(tcfg_gnt_pending),
        .I2(cur_state),
        .I3(pcie_block_i_i_38_n_0),
        .I4(ppm_L23_thrtl),
        .I5(tcfg_req_thrtl),
        .O(cfg_pm_turnoff_ok_n));
  (* SOFT_HLUTNM = "soft_lutpair106" *) 
  LUT4 #(
    .INIT(16'hA202)) 
    pcie_block_i_i_30
       (.I0(tcfg_req_thrtl),
        .I1(pcie_block_i_i_38_n_0),
        .I2(cur_state),
        .I3(tcfg_gnt_pending),
        .O(trn_tcfg_gnt));
  (* SOFT_HLUTNM = "soft_lutpair102" *) 
  LUT5 #(
    .INIT(32'hFFFF20E0)) 
    pcie_block_i_i_38
       (.I0(reg_axi_in_pkt),
        .I1(s_axis_tx_tvalid),
        .I2(tready_thrtl_reg_0),
        .I3(s_axis_tx_tlast),
        .I4(cur_state_i_2_n_0),
        .O(pcie_block_i_i_38_n_0));
  LUT6 #(
    .INIT(64'h0000010000000000)) 
    ppm_L1_thrtl_i_2
       (.I0(cfg_pcie_link_state_d[1]),
        .I1(cfg_pcie_link_state_d[2]),
        .I2(cfg_pcie_link_state_d[0]),
        .I3(cfg_pcie_link_state[0]),
        .I4(cfg_pcie_link_state[1]),
        .I5(cfg_pcie_link_state[2]),
        .O(ppm_L1_trig));
  FDRE ppm_L1_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(ppm_L1_thrtl_reg_0),
        .Q(ppm_L1_thrtl),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair104" *) 
  LUT3 #(
    .INIT(8'hF8)) 
    ppm_L23_thrtl_i_1
       (.I0(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ),
        .I1(reg_turnoff_ok),
        .I2(ppm_L23_thrtl),
        .O(ppm_L23_thrtl_i_1_n_0));
  FDRE ppm_L23_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(ppm_L23_thrtl_i_1_n_0),
        .Q(ppm_L23_thrtl),
        .R(SR));
  LUT5 #(
    .INIT(32'h00005F40)) 
    reg_axi_in_pkt_i_1
       (.I0(s_axis_tx_tlast),
        .I1(tready_thrtl_reg_0),
        .I2(s_axis_tx_tvalid),
        .I3(reg_axi_in_pkt),
        .I4(SR),
        .O(reg_axi_in_pkt_i_1_n_0));
  FDRE reg_axi_in_pkt_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(reg_axi_in_pkt_i_1_n_0),
        .Q(reg_axi_in_pkt),
        .R(1'b0));
  FDRE reg_tcfg_gnt_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tx_cfg_gnt),
        .Q(reg_tcfg_gnt),
        .R(SR));
  FDRE \tbuf_av_d_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[0]),
        .Q(tbuf_av_d[0]),
        .R(SR));
  FDRE \tbuf_av_d_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[1]),
        .Q(tbuf_av_d[1]),
        .R(SR));
  FDRE \tbuf_av_d_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[2]),
        .Q(tbuf_av_d[2]),
        .R(SR));
  FDRE \tbuf_av_d_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[3]),
        .Q(tbuf_av_d[3]),
        .R(SR));
  FDRE \tbuf_av_d_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[4]),
        .Q(tbuf_av_d[4]),
        .R(SR));
  FDRE \tbuf_av_d_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tbuf_av[5]),
        .Q(tbuf_av_d[5]),
        .R(SR));
  LUT3 #(
    .INIT(8'hEA)) 
    tbuf_av_gap_thrtl_i_1
       (.I0(tbuf_av_gap_trig),
        .I1(\tbuf_gap_cnt_reg_n_0_[0] ),
        .I2(tbuf_av_gap_thrtl),
        .O(tbuf_av_gap_thrtl_i_1_n_0));
  FDRE tbuf_av_gap_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tbuf_av_gap_thrtl_i_1_n_0),
        .Q(tbuf_av_gap_thrtl),
        .R(SR));
  FDRE tbuf_av_min_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tbuf_av_min_trig),
        .Q(tbuf_av_min_thrtl),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair106" *) 
  LUT2 #(
    .INIT(4'h7)) 
    \tbuf_gap_cnt[0]_i_1 
       (.I0(tbuf_av_gap_thrtl),
        .I1(cur_state),
        .O(\tbuf_gap_cnt[0]_i_1_n_0 ));
  FDRE \tbuf_gap_cnt_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\tbuf_gap_cnt[0]_i_1_n_0 ),
        .Q(\tbuf_gap_cnt_reg_n_0_[0] ),
        .R(SR));
  LUT6 #(
    .INIT(64'h44F44444F4F4F4F4)) 
    tcfg_gnt_pending_i_1
       (.I0(trn_tcfg_req_d),
        .I1(trn_tcfg_req),
        .I2(tcfg_gnt_pending),
        .I3(cur_state),
        .I4(pcie_block_i_i_38_n_0),
        .I5(tcfg_req_thrtl),
        .O(tcfg_gnt_pending_i_1_n_0));
  FDRE tcfg_gnt_pending_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tcfg_gnt_pending_i_1_n_0),
        .Q(tcfg_gnt_pending),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000000000000D00)) 
    \tcfg_req_cnt[0]_i_1 
       (.I0(trn_tcfg_req),
        .I1(trn_tcfg_req_d),
        .I2(tcfg_gnt_pending),
        .I3(tcfg_req_cnt[1]),
        .I4(tcfg_req_cnt[0]),
        .I5(SR),
        .O(\tcfg_req_cnt[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair103" *) 
  LUT5 #(
    .INIT(32'hFFFF88F8)) 
    \tcfg_req_cnt[1]_i_1 
       (.I0(tcfg_req_cnt[0]),
        .I1(tcfg_req_cnt[1]),
        .I2(trn_tcfg_req),
        .I3(trn_tcfg_req_d),
        .I4(tcfg_gnt_pending),
        .O(\tcfg_req_cnt[1]_i_1_n_0 ));
  FDRE \tcfg_req_cnt_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\tcfg_req_cnt[0]_i_1_n_0 ),
        .Q(tcfg_req_cnt[0]),
        .R(1'b0));
  FDRE \tcfg_req_cnt_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(\tcfg_req_cnt[1]_i_1_n_0 ),
        .Q(tcfg_req_cnt[1]),
        .R(SR));
  LUT6 #(
    .INIT(64'hFFFFF8FF88888888)) 
    tcfg_req_thrtl_i_1
       (.I0(reg_tcfg_gnt),
        .I1(trn_tcfg_req),
        .I2(trn_tdst_rdy_d),
        .I3(trn_tdst_rdy),
        .I4(p_2_in),
        .I5(tcfg_req_thrtl),
        .O(tcfg_req_thrtl_i_1_n_0));
  (* SOFT_HLUTNM = "soft_lutpair103" *) 
  LUT2 #(
    .INIT(4'hE)) 
    tcfg_req_thrtl_i_2
       (.I0(tcfg_req_cnt[1]),
        .I1(tcfg_req_cnt[0]),
        .O(p_2_in));
  FDRE tcfg_req_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tcfg_req_thrtl_i_1_n_0),
        .Q(tcfg_req_thrtl),
        .R(SR));
  LUT4 #(
    .INIT(16'h0080)) 
    \throttle_ctl_pipeline.reg_tsrc_rdy_i_1 
       (.I0(tready_thrtl_reg_0),
        .I1(s_axis_tx_tvalid),
        .I2(out),
        .I3(reg_disable_trn),
        .O(reg_tsrc_rdy0));
  LUT6 #(
    .INIT(64'hF1F1F1F10000F100)) 
    tready_thrtl_i_1
       (.I0(\ecrc_pause_enabled.reg_tx_ecrc_pkt ),
        .I1(tready_thrtl_i_2_n_0),
        .I2(tready_thrtl_i_3_n_0),
        .I3(tready_thrtl_i_4_n_0),
        .I4(tbuf_av_gap_trig),
        .I5(tready_thrtl_i_6_n_0),
        .O(tready_thrtl0));
  LUT6 #(
    .INIT(64'h00002000AAAAAAAA)) 
    tready_thrtl_i_10
       (.I0(tready_thrtl_i_5_0),
        .I1(tbuf_av_d[4]),
        .I2(tbuf_av_d[0]),
        .I3(tbuf_av_d[1]),
        .I4(tready_thrtl_i_12_n_0),
        .I5(tready_thrtl_i_3_n_0),
        .O(tready_thrtl_i_10_n_0));
  LUT4 #(
    .INIT(16'hFFEF)) 
    tready_thrtl_i_12
       (.I0(tbuf_av_d[5]),
        .I1(tbuf_av_d[2]),
        .I2(trn_tbuf_av[1]),
        .I3(tbuf_av_d[3]),
        .O(tready_thrtl_i_12_n_0));
  (* SOFT_HLUTNM = "soft_lutpair105" *) 
  LUT4 #(
    .INIT(16'h0078)) 
    tready_thrtl_i_2
       (.I0(s_axis_tx_tdata[0]),
        .I1(s_axis_tx_tdata[3]),
        .I2(s_axis_tx_tdata[2]),
        .I3(tready_thrtl_i_7_n_0),
        .O(tready_thrtl_i_2_n_0));
  (* SOFT_HLUTNM = "soft_lutpair102" *) 
  LUT3 #(
    .INIT(8'h7F)) 
    tready_thrtl_i_3
       (.I0(s_axis_tx_tlast),
        .I1(s_axis_tx_tvalid),
        .I2(tready_thrtl_reg_0),
        .O(tready_thrtl_i_3_n_0));
  LUT6 #(
    .INIT(64'h0000000000040000)) 
    tready_thrtl_i_4
       (.I0(ppm_L23_trig),
        .I1(out),
        .I2(tcfg_req_trig),
        .I3(ppm_L1_trig),
        .I4(cur_state_i_2_n_0),
        .I5(tbuf_av_min_trig),
        .O(tready_thrtl_i_4_n_0));
  LUT6 #(
    .INIT(64'hFFFFFFFF00100000)) 
    tready_thrtl_i_5
       (.I0(tcfg_req_cnt[0]),
        .I1(tcfg_req_cnt[1]),
        .I2(trn_tdst_rdy),
        .I3(trn_tdst_rdy_d),
        .I4(tcfg_req_thrtl),
        .I5(tready_thrtl_i_10_n_0),
        .O(tbuf_av_gap_trig));
  LUT5 #(
    .INIT(32'h000020E0)) 
    tready_thrtl_i_6
       (.I0(reg_axi_in_pkt),
        .I1(s_axis_tx_tvalid),
        .I2(tready_thrtl_reg_0),
        .I3(s_axis_tx_tlast),
        .I4(cur_state),
        .O(tready_thrtl_i_6_n_0));
  LUT5 #(
    .INIT(32'hFFFFDFFF)) 
    tready_thrtl_i_7
       (.I0(s_axis_tx_tuser),
        .I1(s_axis_tx_tdata[1]),
        .I2(s_axis_tx_tvalid),
        .I3(tready_thrtl_reg_0),
        .I4(reg_axi_in_pkt),
        .O(tready_thrtl_i_7_n_0));
  (* SOFT_HLUTNM = "soft_lutpair107" *) 
  LUT2 #(
    .INIT(4'h8)) 
    tready_thrtl_i_8
       (.I0(reg_turnoff_ok),
        .I1(\L23_thrtl_ep.x7_L23_thrtl_ep.reg_to_turnoff ),
        .O(ppm_L23_trig));
  FDRE tready_thrtl_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(tready_thrtl0),
        .Q(tready_thrtl_reg_0),
        .R(SR));
  FDRE trn_tcfg_req_d_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tcfg_req),
        .Q(trn_tcfg_req_d),
        .R(SR));
  FDSE trn_tdst_rdy_d_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_tdst_rdy),
        .Q(trn_tdst_rdy_d),
        .S(SR));
endmodule

module pcie_7x_bridge_core_top
   (pl_ltssm_state,
    user_reset_out,
    m_axis_rx_tvalid,
    s_axis_tx_tready,
    pl_phy_lnk_up,
    cfg_aer_ecrc_check_en,
    cfg_aer_ecrc_gen_en,
    cfg_aer_rooterr_corr_err_received,
    cfg_aer_rooterr_corr_err_reporting_en,
    cfg_aer_rooterr_fatal_err_received,
    cfg_aer_rooterr_fatal_err_reporting_en,
    cfg_aer_rooterr_non_fatal_err_received,
    cfg_aer_rooterr_non_fatal_err_reporting_en,
    cfg_bridge_serr_en,
    cfg_command,
    cfg_dcommand2,
    cfg_dcommand,
    cfg_dstatus,
    cfg_interrupt_msienable,
    cfg_interrupt_msixenable,
    cfg_interrupt_msixfm,
    cfg_lcommand,
    cfg_lstatus,
    cfg_msg_received,
    cfg_msg_received_assert_int_a,
    cfg_msg_received_assert_int_b,
    cfg_msg_received_assert_int_c,
    cfg_msg_received_assert_int_d,
    cfg_msg_received_deassert_int_a,
    cfg_msg_received_deassert_int_b,
    cfg_msg_received_deassert_int_c,
    cfg_msg_received_deassert_int_d,
    cfg_msg_received_err_cor,
    cfg_msg_received_err_fatal,
    cfg_msg_received_err_non_fatal,
    cfg_msg_received_pm_as_nak,
    cfg_to_turnoff,
    cfg_msg_received_pme_to_ack,
    cfg_msg_received_pm_pme,
    cfg_msg_received_setslotpowerlimit,
    cfg_pmcsr_pme_en,
    cfg_pmcsr_pme_status,
    cfg_root_control_pme_int_en,
    cfg_root_control_syserr_corr_err_en,
    cfg_root_control_syserr_fatal_err_en,
    cfg_root_control_syserr_non_fatal_err_en,
    cfg_slot_control_electromech_il_ctl_pulse,
    pcie_drp_rdy,
    pl_directed_change_done,
    pl_link_gen2_cap,
    pl_link_partner_gen2_supported,
    pl_link_upcfg_cap,
    pl_sel_lnk_rate,
    tx_cfg_req,
    tx_err_drop,
    fc_cpld,
    fc_npd,
    fc_pd,
    cfg_msg_data,
    pcie_drp_do,
    cfg_pmcsr_powerstate,
    pl_lane_reversal_mode,
    pl_rx_pm_state,
    pl_sel_lnk_width,
    cfg_interrupt_mmenable,
    cfg_pcie_link_state,
    pl_initial_link_width,
    pl_tx_pm_state,
    cfg_mgmt_do,
    tx_buf_av,
    cfg_vc_tcvc_map,
    cfg_interrupt_do,
    fc_cplh,
    fc_nph,
    fc_ph,
    m_axis_rx_tdata,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
    m_axis_rx_tuser,
    cfg_bus_number,
    cfg_device_number,
    cfg_function_number,
    user_lnk_up,
    cfg_mgmt_rd_wr_done,
    cfg_err_aer_headerlog_set,
    cfg_err_cpl_rdy,
    cfg_interrupt_rdy,
    cfg_received_func_lvl_rst,
    pci_exp_txn,
    pci_exp_txp,
    pipe_rxoutclk_out,
    pipe_txoutclk_out,
    pipe_pclk_sel_out,
    pl_received_hot_rst,
    pipe_pclk_in,
    m_axis_rx_tready,
    s_axis_tx_tlast,
    s_axis_tx_tvalid,
    pipe_userclk2_in,
    pipe_userclk1_in,
    pcie_drp_clk,
    pcie_drp_en,
    pcie_drp_we,
    pl_directed_link_auton,
    pl_directed_link_speed,
    pl_downstream_deemph_source,
    pl_transmit_hot_rst,
    pl_upstream_prefer_deemph,
    rx_np_ok,
    rx_np_req,
    cfg_err_aer_headerlog,
    pcie_drp_di,
    cfg_pm_force_state,
    pl_directed_link_change,
    pl_directed_link_width,
    cfg_ds_function_number,
    fc_sel,
    cfg_mgmt_di,
    cfg_err_tlp_cpl_header,
    cfg_aer_interrupt_msgnum,
    cfg_ds_device_number,
    cfg_pciecap_interrupt_msgnum,
    cfg_dsn,
    cfg_ds_bus_number,
    cfg_interrupt_di,
    pcie_drp_addr,
    cfg_mgmt_dwaddr,
    tx_cfg_gnt,
    cfg_turnoff_ok,
    s_axis_tx_tdata,
    s_axis_tx_tuser,
    s_axis_tx_tkeep,
    cfg_trn_pending,
    pipe_dclk_in,
    sys_clk,
    pci_exp_rxn,
    pci_exp_rxp,
    pipe_rxusrclk_in,
    pipe_mmcm_lock_in,
    pipe_oobclk_in,
    cfg_mgmt_byte_en,
    sys_rst_n,
    cfg_mgmt_wr_rw1c_as_rw,
    cfg_mgmt_wr_readonly,
    cfg_mgmt_wr_en,
    cfg_mgmt_rd_en,
    cfg_err_malformed,
    cfg_err_cor,
    cfg_err_ur,
    cfg_err_ecrc,
    cfg_err_cpl_timeout,
    cfg_err_cpl_abort,
    cfg_err_cpl_unexpect,
    cfg_err_poisoned,
    cfg_err_atomic_egress_blocked,
    cfg_err_mc_blocked,
    cfg_err_internal_uncor,
    cfg_err_internal_cor,
    cfg_err_posted,
    cfg_err_locked,
    cfg_err_norecovery,
    cfg_interrupt,
    cfg_interrupt_assert,
    cfg_interrupt_stat,
    cfg_pm_halt_aspm_l0s,
    cfg_pm_halt_aspm_l1,
    cfg_pm_force_state_en,
    cfg_pm_wake);
  output [5:0]pl_ltssm_state;
  output user_reset_out;
  output m_axis_rx_tvalid;
  output s_axis_tx_tready;
  output pl_phy_lnk_up;
  output cfg_aer_ecrc_check_en;
  output cfg_aer_ecrc_gen_en;
  output cfg_aer_rooterr_corr_err_received;
  output cfg_aer_rooterr_corr_err_reporting_en;
  output cfg_aer_rooterr_fatal_err_received;
  output cfg_aer_rooterr_fatal_err_reporting_en;
  output cfg_aer_rooterr_non_fatal_err_received;
  output cfg_aer_rooterr_non_fatal_err_reporting_en;
  output cfg_bridge_serr_en;
  output [4:0]cfg_command;
  output [11:0]cfg_dcommand2;
  output [14:0]cfg_dcommand;
  output [3:0]cfg_dstatus;
  output cfg_interrupt_msienable;
  output cfg_interrupt_msixenable;
  output cfg_interrupt_msixfm;
  output [10:0]cfg_lcommand;
  output [9:0]cfg_lstatus;
  output cfg_msg_received;
  output cfg_msg_received_assert_int_a;
  output cfg_msg_received_assert_int_b;
  output cfg_msg_received_assert_int_c;
  output cfg_msg_received_assert_int_d;
  output cfg_msg_received_deassert_int_a;
  output cfg_msg_received_deassert_int_b;
  output cfg_msg_received_deassert_int_c;
  output cfg_msg_received_deassert_int_d;
  output cfg_msg_received_err_cor;
  output cfg_msg_received_err_fatal;
  output cfg_msg_received_err_non_fatal;
  output cfg_msg_received_pm_as_nak;
  output cfg_to_turnoff;
  output cfg_msg_received_pme_to_ack;
  output cfg_msg_received_pm_pme;
  output cfg_msg_received_setslotpowerlimit;
  output cfg_pmcsr_pme_en;
  output cfg_pmcsr_pme_status;
  output cfg_root_control_pme_int_en;
  output cfg_root_control_syserr_corr_err_en;
  output cfg_root_control_syserr_fatal_err_en;
  output cfg_root_control_syserr_non_fatal_err_en;
  output cfg_slot_control_electromech_il_ctl_pulse;
  output pcie_drp_rdy;
  output pl_directed_change_done;
  output pl_link_gen2_cap;
  output pl_link_partner_gen2_supported;
  output pl_link_upcfg_cap;
  output pl_sel_lnk_rate;
  output tx_cfg_req;
  output tx_err_drop;
  output [11:0]fc_cpld;
  output [11:0]fc_npd;
  output [11:0]fc_pd;
  output [15:0]cfg_msg_data;
  output [15:0]pcie_drp_do;
  output [1:0]cfg_pmcsr_powerstate;
  output [1:0]pl_lane_reversal_mode;
  output [1:0]pl_rx_pm_state;
  output [1:0]pl_sel_lnk_width;
  output [2:0]cfg_interrupt_mmenable;
  output [2:0]cfg_pcie_link_state;
  output [2:0]pl_initial_link_width;
  output [2:0]pl_tx_pm_state;
  output [31:0]cfg_mgmt_do;
  output [5:0]tx_buf_av;
  output [6:0]cfg_vc_tcvc_map;
  output [7:0]cfg_interrupt_do;
  output [7:0]fc_cplh;
  output [7:0]fc_nph;
  output [7:0]fc_ph;
  output [63:0]m_axis_rx_tdata;
  output [0:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output [12:0]m_axis_rx_tuser;
  output [7:0]cfg_bus_number;
  output [4:0]cfg_device_number;
  output [2:0]cfg_function_number;
  output user_lnk_up;
  output cfg_mgmt_rd_wr_done;
  output cfg_err_aer_headerlog_set;
  output cfg_err_cpl_rdy;
  output cfg_interrupt_rdy;
  output cfg_received_func_lvl_rst;
  output [0:0]pci_exp_txn;
  output [0:0]pci_exp_txp;
  output [0:0]pipe_rxoutclk_out;
  output pipe_txoutclk_out;
  output [0:0]pipe_pclk_sel_out;
  output pl_received_hot_rst;
  input pipe_pclk_in;
  input m_axis_rx_tready;
  input s_axis_tx_tlast;
  input s_axis_tx_tvalid;
  input pipe_userclk2_in;
  input pipe_userclk1_in;
  input pcie_drp_clk;
  input pcie_drp_en;
  input pcie_drp_we;
  input pl_directed_link_auton;
  input pl_directed_link_speed;
  input pl_downstream_deemph_source;
  input pl_transmit_hot_rst;
  input pl_upstream_prefer_deemph;
  input rx_np_ok;
  input rx_np_req;
  input [127:0]cfg_err_aer_headerlog;
  input [15:0]pcie_drp_di;
  input [1:0]cfg_pm_force_state;
  input [1:0]pl_directed_link_change;
  input [1:0]pl_directed_link_width;
  input [2:0]cfg_ds_function_number;
  input [2:0]fc_sel;
  input [31:0]cfg_mgmt_di;
  input [47:0]cfg_err_tlp_cpl_header;
  input [4:0]cfg_aer_interrupt_msgnum;
  input [4:0]cfg_ds_device_number;
  input [4:0]cfg_pciecap_interrupt_msgnum;
  input [63:0]cfg_dsn;
  input [7:0]cfg_ds_bus_number;
  input [7:0]cfg_interrupt_di;
  input [8:0]pcie_drp_addr;
  input [9:0]cfg_mgmt_dwaddr;
  input tx_cfg_gnt;
  input cfg_turnoff_ok;
  input [63:0]s_axis_tx_tdata;
  input [3:0]s_axis_tx_tuser;
  input [0:0]s_axis_tx_tkeep;
  input cfg_trn_pending;
  input pipe_dclk_in;
  input sys_clk;
  input [0:0]pci_exp_rxn;
  input [0:0]pci_exp_rxp;
  input pipe_rxusrclk_in;
  input pipe_mmcm_lock_in;
  input pipe_oobclk_in;
  input [3:0]cfg_mgmt_byte_en;
  input sys_rst_n;
  input cfg_mgmt_wr_rw1c_as_rw;
  input cfg_mgmt_wr_readonly;
  input cfg_mgmt_wr_en;
  input cfg_mgmt_rd_en;
  input cfg_err_malformed;
  input cfg_err_cor;
  input cfg_err_ur;
  input cfg_err_ecrc;
  input cfg_err_cpl_timeout;
  input cfg_err_cpl_abort;
  input cfg_err_cpl_unexpect;
  input cfg_err_poisoned;
  input cfg_err_atomic_egress_blocked;
  input cfg_err_mc_blocked;
  input cfg_err_internal_uncor;
  input cfg_err_internal_cor;
  input cfg_err_posted;
  input cfg_err_locked;
  input cfg_err_norecovery;
  input cfg_interrupt;
  input cfg_interrupt_assert;
  input cfg_interrupt_stat;
  input cfg_pm_halt_aspm_l0s;
  input cfg_pm_halt_aspm_l1;
  input cfg_pm_force_state_en;
  input cfg_pm_wake;

  wire bridge_reset_int;
  wire cfg_aer_ecrc_check_en;
  wire cfg_aer_ecrc_gen_en;
  wire [4:0]cfg_aer_interrupt_msgnum;
  wire cfg_aer_rooterr_corr_err_received;
  wire cfg_aer_rooterr_corr_err_reporting_en;
  wire cfg_aer_rooterr_fatal_err_received;
  wire cfg_aer_rooterr_fatal_err_reporting_en;
  wire cfg_aer_rooterr_non_fatal_err_received;
  wire cfg_aer_rooterr_non_fatal_err_reporting_en;
  wire cfg_bridge_serr_en;
  wire [7:0]cfg_bus_number;
  wire [4:0]cfg_command;
  wire [14:0]cfg_dcommand;
  wire [11:0]cfg_dcommand2;
  wire [4:0]cfg_device_number;
  wire [7:0]cfg_ds_bus_number;
  wire [4:0]cfg_ds_device_number;
  wire [2:0]cfg_ds_function_number;
  wire [63:0]cfg_dsn;
  wire [3:0]cfg_dstatus;
  wire [127:0]cfg_err_aer_headerlog;
  wire cfg_err_aer_headerlog_set;
  wire cfg_err_atomic_egress_blocked;
  wire cfg_err_cor;
  wire cfg_err_cpl_abort;
  wire cfg_err_cpl_rdy;
  wire cfg_err_cpl_timeout;
  wire cfg_err_cpl_unexpect;
  wire cfg_err_ecrc;
  wire cfg_err_internal_cor;
  wire cfg_err_internal_uncor;
  wire cfg_err_locked;
  wire cfg_err_malformed;
  wire cfg_err_mc_blocked;
  wire cfg_err_norecovery;
  wire cfg_err_poisoned;
  wire cfg_err_posted;
  wire [47:0]cfg_err_tlp_cpl_header;
  wire cfg_err_ur;
  wire [2:0]cfg_function_number;
  wire cfg_interrupt;
  wire cfg_interrupt_assert;
  wire [7:0]cfg_interrupt_di;
  wire [7:0]cfg_interrupt_do;
  wire [2:0]cfg_interrupt_mmenable;
  wire cfg_interrupt_msienable;
  wire cfg_interrupt_msixenable;
  wire cfg_interrupt_msixfm;
  wire cfg_interrupt_rdy;
  wire cfg_interrupt_stat;
  wire [10:0]cfg_lcommand;
  wire [9:0]cfg_lstatus;
  wire [3:0]cfg_mgmt_byte_en;
  wire [31:0]cfg_mgmt_di;
  wire [31:0]cfg_mgmt_do;
  wire [9:0]cfg_mgmt_dwaddr;
  wire cfg_mgmt_rd_en;
  wire cfg_mgmt_rd_wr_done;
  wire cfg_mgmt_wr_en;
  wire cfg_mgmt_wr_readonly;
  wire cfg_mgmt_wr_rw1c_as_rw;
  wire [15:0]cfg_msg_data;
  wire cfg_msg_received;
  wire cfg_msg_received_assert_int_a;
  wire cfg_msg_received_assert_int_b;
  wire cfg_msg_received_assert_int_c;
  wire cfg_msg_received_assert_int_d;
  wire cfg_msg_received_deassert_int_a;
  wire cfg_msg_received_deassert_int_b;
  wire cfg_msg_received_deassert_int_c;
  wire cfg_msg_received_deassert_int_d;
  wire cfg_msg_received_err_cor;
  wire cfg_msg_received_err_fatal;
  wire cfg_msg_received_err_non_fatal;
  wire cfg_msg_received_pm_as_nak;
  wire cfg_msg_received_pm_pme;
  wire cfg_msg_received_pme_to_ack;
  wire cfg_msg_received_setslotpowerlimit;
  wire [2:0]cfg_pcie_link_state;
  wire [4:0]cfg_pciecap_interrupt_msgnum;
  wire [1:0]cfg_pm_force_state;
  wire cfg_pm_force_state_en;
  wire cfg_pm_halt_aspm_l0s;
  wire cfg_pm_halt_aspm_l1;
  wire cfg_pm_wake;
  wire cfg_pmcsr_pme_en;
  wire cfg_pmcsr_pme_status;
  wire [1:0]cfg_pmcsr_powerstate;
  wire cfg_received_func_lvl_rst;
  wire cfg_root_control_pme_int_en;
  wire cfg_root_control_syserr_corr_err_en;
  wire cfg_root_control_syserr_fatal_err_en;
  wire cfg_root_control_syserr_non_fatal_err_en;
  wire cfg_slot_control_electromech_il_ctl_pulse;
  wire cfg_to_turnoff;
  wire cfg_trn_pending;
  wire cfg_turnoff_ok;
  wire [6:0]cfg_vc_tcvc_map;
  wire [11:0]fc_cpld;
  wire [7:0]fc_cplh;
  wire [11:0]fc_npd;
  wire [7:0]fc_nph;
  wire [11:0]fc_pd;
  wire [7:0]fc_ph;
  wire [2:0]fc_sel;
  wire gt_top_i_n_0;
  wire \ltssm_reg1_reg[0]_srl2_n_0 ;
  wire \ltssm_reg1_reg[1]_srl2_n_0 ;
  wire \ltssm_reg1_reg[2]_srl2_n_0 ;
  wire \ltssm_reg1_reg[3]_srl2_n_0 ;
  wire \ltssm_reg1_reg[4]_srl2_n_0 ;
  wire \ltssm_reg1_reg[5]_srl2_n_0 ;
  wire [5:0]ltssm_reg2;
  wire [63:0]m_axis_rx_tdata;
  wire [0:0]m_axis_rx_tkeep;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [12:0]m_axis_rx_tuser;
  wire m_axis_rx_tvalid;
  wire p_0_in_0;
  wire \p_0_out_inferred__0/store_ltssm_inferred_i_2_n_0 ;
  wire \p_0_out_inferred__0/store_ltssm_inferred_i_3_n_0 ;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire pcie_block_i_i_34_n_0;
  wire pcie_block_i_i_35_n_0;
  wire pcie_block_i_i_36_n_0;
  wire pcie_block_i_i_37_n_0;
  wire [8:0]pcie_drp_addr;
  wire pcie_drp_clk;
  wire [15:0]pcie_drp_di;
  wire [15:0]pcie_drp_do;
  wire pcie_drp_en;
  wire pcie_drp_rdy;
  wire pcie_drp_we;
  wire pcie_top_i_n_5;
  wire pipe_dclk_in;
  wire pipe_mmcm_lock_in;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire pipe_rx0_chanisaligned_gt;
  wire [1:0]pipe_rx0_char_is_k_gt;
  wire [15:0]pipe_rx0_data_gt;
  wire pipe_rx0_elec_idle_gt;
  wire pipe_rx0_phy_status_gt;
  wire pipe_rx0_polarity_gt;
  wire [2:0]pipe_rx0_status_gt;
  wire pipe_rx0_valid_gt;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire [1:0]pipe_tx0_char_is_k_gt;
  wire pipe_tx0_compliance_gt;
  wire [15:0]pipe_tx0_data_gt;
  wire pipe_tx0_elec_idle_gt;
  wire [1:0]pipe_tx0_powerdown_gt;
  wire pipe_tx_deemph_gt;
  wire [2:0]pipe_tx_margin_gt;
  wire pipe_tx_rate_gt;
  wire pipe_tx_rcvr_det_gt;
  wire pipe_txoutclk_out;
  wire pipe_userclk1_in;
  wire pipe_userclk2_in;
  wire pl_directed_change_done;
  wire pl_directed_link_auton;
  wire [1:0]pl_directed_link_change;
  wire pl_directed_link_speed;
  wire [1:0]pl_directed_link_width;
  wire pl_downstream_deemph_source;
  wire [2:0]pl_initial_link_width;
  wire [1:0]pl_lane_reversal_mode;
  wire pl_link_gen2_cap;
  wire pl_link_partner_gen2_supported;
  wire pl_link_upcfg_cap;
  wire [5:0]pl_ltssm_state;
  wire pl_phy_lnk_up;
  wire pl_phy_lnk_up_sync;
  wire pl_phy_lnk_up_wire;
  wire pl_received_hot_rst;
  wire pl_received_hot_rst_sync;
  wire pl_received_hot_rst_wire;
  wire [1:0]pl_rx_pm_state;
  wire pl_sel_lnk_rate;
  wire [1:0]pl_sel_lnk_width;
  wire pl_transmit_hot_rst;
  wire [2:0]pl_tx_pm_state;
  wire pl_upstream_prefer_deemph;
  wire rx_np_ok;
  wire rx_np_req;
  wire [63:0]s_axis_tx_tdata;
  wire [0:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire s_axis_tx_tready;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  (* DONT_TOUCH *) wire store_ltssm;
  wire sys_clk;
  wire sys_or_hot_rst;
  wire sys_rst_n;
  wire trn_lnk_up;
  wire [5:0]tx_buf_av;
  wire tx_cfg_gnt;
  wire tx_cfg_req;
  wire tx_err_drop;
  (* RTL_KEEP = "true" *) (* async_reg = "true" *) wire user_lnk_up_int;
  (* async_reg = "true" *) wire user_lnk_up_mux;
  wire user_reset_out;

  assign user_lnk_up = user_lnk_up_int;
  pcie_7x_bridge_gt_top gt_top_i
       (.p_0_in_0(p_0_in_0),
        .pci_exp_rxn(pci_exp_rxn),
        .pci_exp_rxp(pci_exp_rxp),
        .pci_exp_txn(pci_exp_txn),
        .pci_exp_txp(pci_exp_txp),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_oobclk_in(pipe_oobclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .pipe_rx0_chanisaligned(pipe_rx0_chanisaligned_gt),
        .pipe_rx0_char_is_k(pipe_rx0_char_is_k_gt),
        .pipe_rx0_data(pipe_rx0_data_gt),
        .pipe_rx0_elec_idle(pipe_rx0_elec_idle_gt),
        .pipe_rx0_phy_status(pipe_rx0_phy_status_gt),
        .pipe_rx0_polarity(pipe_rx0_polarity_gt),
        .pipe_rx0_status(pipe_rx0_status_gt),
        .pipe_rx0_valid(pipe_rx0_valid_gt),
        .pipe_rxoutclk_out(pipe_rxoutclk_out),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_tx0_char_is_k(pipe_tx0_char_is_k_gt),
        .pipe_tx0_compliance(pipe_tx0_compliance_gt),
        .pipe_tx0_data(pipe_tx0_data_gt),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle_gt),
        .pipe_tx0_powerdown(pipe_tx0_powerdown_gt),
        .pipe_tx_deemph(pipe_tx_deemph_gt),
        .pipe_tx_margin(pipe_tx_margin_gt),
        .pipe_tx_rate(pipe_tx_rate_gt),
        .pipe_tx_rcvr_det(pipe_tx_rcvr_det_gt),
        .pipe_txoutclk_out(pipe_txoutclk_out),
        .pl_ltssm_state(pl_ltssm_state),
        .reset_n_reg1_reg(sys_rst_n),
        .sys_clk(sys_clk),
        .sys_rst_n(gt_top_i_n_0));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[0]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[0]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[0]),
        .Q(\ltssm_reg1_reg[0]_srl2_n_0 ));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[1]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[1]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[1]),
        .Q(\ltssm_reg1_reg[1]_srl2_n_0 ));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[2]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[2]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[2]),
        .Q(\ltssm_reg1_reg[2]_srl2_n_0 ));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[3]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[3]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[3]),
        .Q(\ltssm_reg1_reg[3]_srl2_n_0 ));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[4]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[4]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[4]),
        .Q(\ltssm_reg1_reg[4]_srl2_n_0 ));
  (* srl_bus_name = "inst/\\inst/ltssm_reg1_reg " *) 
  (* srl_name = "inst/\\inst/ltssm_reg1_reg[5]_srl2 " *) 
  SRL16E #(
    .INIT(16'h0000)) 
    \ltssm_reg1_reg[5]_srl2 
       (.A0(1'b1),
        .A1(1'b0),
        .A2(1'b0),
        .A3(1'b0),
        .CE(1'b1),
        .CLK(pipe_pclk_in),
        .D(pl_ltssm_state[5]),
        .Q(\ltssm_reg1_reg[5]_srl2_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[0]_srl2_n_0 ),
        .Q(ltssm_reg2[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[1]_srl2_n_0 ),
        .Q(ltssm_reg2[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[2]_srl2_n_0 ),
        .Q(ltssm_reg2[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[3]_srl2_n_0 ),
        .Q(ltssm_reg2[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[4]_srl2_n_0 ),
        .Q(ltssm_reg2[4]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \ltssm_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\ltssm_reg1_reg[5]_srl2_n_0 ),
        .Q(ltssm_reg2[5]),
        .R(1'b0));
  LUT2 #(
    .INIT(4'hE)) 
    \p_0_out_inferred__0/store_ltssm_inferred_i_1 
       (.I0(\p_0_out_inferred__0/store_ltssm_inferred_i_2_n_0 ),
        .I1(\p_0_out_inferred__0/store_ltssm_inferred_i_3_n_0 ),
        .O(store_ltssm));
  LUT6 #(
    .INIT(64'h6FF6FFFFFFFF6FF6)) 
    \p_0_out_inferred__0/store_ltssm_inferred_i_2 
       (.I0(ltssm_reg2[0]),
        .I1(pl_ltssm_state[0]),
        .I2(pl_ltssm_state[2]),
        .I3(ltssm_reg2[2]),
        .I4(pl_ltssm_state[1]),
        .I5(ltssm_reg2[1]),
        .O(\p_0_out_inferred__0/store_ltssm_inferred_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h6FF6FFFFFFFF6FF6)) 
    \p_0_out_inferred__0/store_ltssm_inferred_i_3 
       (.I0(ltssm_reg2[3]),
        .I1(pl_ltssm_state[3]),
        .I2(pl_ltssm_state[5]),
        .I3(ltssm_reg2[5]),
        .I4(pl_ltssm_state[4]),
        .I5(ltssm_reg2[4]),
        .O(\p_0_out_inferred__0/store_ltssm_inferred_i_3_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_34
       (.I0(cfg_mgmt_byte_en[3]),
        .O(pcie_block_i_i_34_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_35
       (.I0(cfg_mgmt_byte_en[2]),
        .O(pcie_block_i_i_35_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_36
       (.I0(cfg_mgmt_byte_en[1]),
        .O(pcie_block_i_i_36_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_37
       (.I0(cfg_mgmt_byte_en[0]),
        .O(pcie_block_i_i_37_n_0));
  pcie_7x_bridge_pcie_top pcie_top_i
       (.SR(user_reset_out),
        .bridge_reset_int(bridge_reset_int),
        .cfg_aer_ecrc_check_en(cfg_aer_ecrc_check_en),
        .cfg_aer_ecrc_gen_en(cfg_aer_ecrc_gen_en),
        .cfg_aer_interrupt_msgnum(cfg_aer_interrupt_msgnum),
        .cfg_aer_rooterr_corr_err_received(cfg_aer_rooterr_corr_err_received),
        .cfg_aer_rooterr_corr_err_reporting_en(cfg_aer_rooterr_corr_err_reporting_en),
        .cfg_aer_rooterr_fatal_err_received(cfg_aer_rooterr_fatal_err_received),
        .cfg_aer_rooterr_fatal_err_reporting_en(cfg_aer_rooterr_fatal_err_reporting_en),
        .cfg_aer_rooterr_non_fatal_err_received(cfg_aer_rooterr_non_fatal_err_received),
        .cfg_aer_rooterr_non_fatal_err_reporting_en(cfg_aer_rooterr_non_fatal_err_reporting_en),
        .cfg_bridge_serr_en(cfg_bridge_serr_en),
        .cfg_bus_number(cfg_bus_number),
        .cfg_command(cfg_command),
        .cfg_dcommand(cfg_dcommand),
        .cfg_dcommand2(cfg_dcommand2),
        .cfg_device_number(cfg_device_number),
        .cfg_ds_bus_number(cfg_ds_bus_number),
        .cfg_ds_device_number(cfg_ds_device_number),
        .cfg_ds_function_number(cfg_ds_function_number),
        .cfg_dsn(cfg_dsn),
        .cfg_dstatus(cfg_dstatus),
        .cfg_err_aer_headerlog(cfg_err_aer_headerlog),
        .cfg_err_aer_headerlog_set(cfg_err_aer_headerlog_set),
        .cfg_err_atomic_egress_blocked(cfg_err_atomic_egress_blocked),
        .cfg_err_cor(cfg_err_cor),
        .cfg_err_cpl_abort(cfg_err_cpl_abort),
        .cfg_err_cpl_rdy(cfg_err_cpl_rdy),
        .cfg_err_cpl_timeout(cfg_err_cpl_timeout),
        .cfg_err_cpl_unexpect(cfg_err_cpl_unexpect),
        .cfg_err_ecrc(cfg_err_ecrc),
        .cfg_err_internal_cor(cfg_err_internal_cor),
        .cfg_err_internal_uncor(cfg_err_internal_uncor),
        .cfg_err_locked(cfg_err_locked),
        .cfg_err_malformed(cfg_err_malformed),
        .cfg_err_mc_blocked(cfg_err_mc_blocked),
        .cfg_err_norecovery(cfg_err_norecovery),
        .cfg_err_poisoned(cfg_err_poisoned),
        .cfg_err_posted(cfg_err_posted),
        .cfg_err_tlp_cpl_header(cfg_err_tlp_cpl_header),
        .cfg_err_ur(cfg_err_ur),
        .cfg_function_number(cfg_function_number),
        .cfg_interrupt(cfg_interrupt),
        .cfg_interrupt_assert(cfg_interrupt_assert),
        .cfg_interrupt_di(cfg_interrupt_di),
        .cfg_interrupt_do(cfg_interrupt_do),
        .cfg_interrupt_mmenable(cfg_interrupt_mmenable),
        .cfg_interrupt_msienable(cfg_interrupt_msienable),
        .cfg_interrupt_msixenable(cfg_interrupt_msixenable),
        .cfg_interrupt_msixfm(cfg_interrupt_msixfm),
        .cfg_interrupt_rdy(cfg_interrupt_rdy),
        .cfg_interrupt_stat(cfg_interrupt_stat),
        .cfg_lcommand(cfg_lcommand),
        .cfg_lstatus(cfg_lstatus),
        .cfg_mgmt_byte_en_n({pcie_block_i_i_34_n_0,pcie_block_i_i_35_n_0,pcie_block_i_i_36_n_0,pcie_block_i_i_37_n_0}),
        .cfg_mgmt_di(cfg_mgmt_di),
        .cfg_mgmt_do(cfg_mgmt_do),
        .cfg_mgmt_dwaddr(cfg_mgmt_dwaddr),
        .cfg_mgmt_rd_en(cfg_mgmt_rd_en),
        .cfg_mgmt_rd_wr_done(cfg_mgmt_rd_wr_done),
        .cfg_mgmt_wr_en(cfg_mgmt_wr_en),
        .cfg_mgmt_wr_readonly(cfg_mgmt_wr_readonly),
        .cfg_mgmt_wr_rw1c_as_rw(cfg_mgmt_wr_rw1c_as_rw),
        .cfg_msg_data(cfg_msg_data),
        .cfg_msg_received(cfg_msg_received),
        .cfg_msg_received_assert_int_a(cfg_msg_received_assert_int_a),
        .cfg_msg_received_assert_int_b(cfg_msg_received_assert_int_b),
        .cfg_msg_received_assert_int_c(cfg_msg_received_assert_int_c),
        .cfg_msg_received_assert_int_d(cfg_msg_received_assert_int_d),
        .cfg_msg_received_deassert_int_a(cfg_msg_received_deassert_int_a),
        .cfg_msg_received_deassert_int_b(cfg_msg_received_deassert_int_b),
        .cfg_msg_received_deassert_int_c(cfg_msg_received_deassert_int_c),
        .cfg_msg_received_deassert_int_d(cfg_msg_received_deassert_int_d),
        .cfg_msg_received_err_cor(cfg_msg_received_err_cor),
        .cfg_msg_received_err_fatal(cfg_msg_received_err_fatal),
        .cfg_msg_received_err_non_fatal(cfg_msg_received_err_non_fatal),
        .cfg_msg_received_pm_as_nak(cfg_msg_received_pm_as_nak),
        .cfg_msg_received_pm_pme(cfg_msg_received_pm_pme),
        .cfg_msg_received_pme_to_ack(cfg_msg_received_pme_to_ack),
        .cfg_msg_received_setslotpowerlimit(cfg_msg_received_setslotpowerlimit),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pciecap_interrupt_msgnum(cfg_pciecap_interrupt_msgnum),
        .cfg_pm_force_state(cfg_pm_force_state),
        .cfg_pm_force_state_en(cfg_pm_force_state_en),
        .cfg_pm_halt_aspm_l0s(cfg_pm_halt_aspm_l0s),
        .cfg_pm_halt_aspm_l1(cfg_pm_halt_aspm_l1),
        .cfg_pm_wake(cfg_pm_wake),
        .cfg_pmcsr_pme_en(cfg_pmcsr_pme_en),
        .cfg_pmcsr_pme_status(cfg_pmcsr_pme_status),
        .cfg_pmcsr_powerstate(cfg_pmcsr_powerstate),
        .cfg_received_func_lvl_rst(cfg_received_func_lvl_rst),
        .cfg_root_control_pme_int_en(cfg_root_control_pme_int_en),
        .cfg_root_control_syserr_corr_err_en(cfg_root_control_syserr_corr_err_en),
        .cfg_root_control_syserr_fatal_err_en(cfg_root_control_syserr_fatal_err_en),
        .cfg_root_control_syserr_non_fatal_err_en(cfg_root_control_syserr_non_fatal_err_en),
        .cfg_slot_control_electromech_il_ctl_pulse(cfg_slot_control_electromech_il_ctl_pulse),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_trn_pending(cfg_trn_pending),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .cfg_vc_tcvc_map(cfg_vc_tcvc_map),
        .fc_cpld(fc_cpld),
        .fc_cplh(fc_cplh),
        .fc_npd(fc_npd),
        .fc_nph(fc_nph),
        .fc_pd(fc_pd),
        .fc_ph(fc_ph),
        .fc_sel(fc_sel),
        .m_axis_rx_tdata(m_axis_rx_tdata),
        .m_axis_rx_tkeep(m_axis_rx_tkeep),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(m_axis_rx_tuser),
        .m_axis_rx_tvalid_reg(m_axis_rx_tvalid),
        .out(user_lnk_up_int),
        .pcie_drp_addr(pcie_drp_addr),
        .pcie_drp_clk(pcie_drp_clk),
        .pcie_drp_di(pcie_drp_di),
        .pcie_drp_do(pcie_drp_do),
        .pcie_drp_en(pcie_drp_en),
        .pcie_drp_rdy(pcie_drp_rdy),
        .pcie_drp_we(pcie_drp_we),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_rx0_chanisaligned(pipe_rx0_chanisaligned_gt),
        .pipe_rx0_char_is_k(pipe_rx0_char_is_k_gt),
        .pipe_rx0_data(pipe_rx0_data_gt),
        .pipe_rx0_elec_idle(pipe_rx0_elec_idle_gt),
        .pipe_rx0_phy_status(pipe_rx0_phy_status_gt),
        .pipe_rx0_polarity(pipe_rx0_polarity_gt),
        .pipe_rx0_status(pipe_rx0_status_gt),
        .pipe_rx0_valid(pipe_rx0_valid_gt),
        .pipe_tx0_char_is_k(pipe_tx0_char_is_k_gt),
        .pipe_tx0_compliance(pipe_tx0_compliance_gt),
        .pipe_tx0_data(pipe_tx0_data_gt),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle_gt),
        .pipe_tx0_powerdown(pipe_tx0_powerdown_gt),
        .pipe_tx_deemph(pipe_tx_deemph_gt),
        .pipe_tx_margin(pipe_tx_margin_gt),
        .pipe_tx_rate(pipe_tx_rate_gt),
        .pipe_tx_rcvr_det(pipe_tx_rcvr_det_gt),
        .pipe_userclk1_in(pipe_userclk1_in),
        .pipe_userclk2_in(pipe_userclk2_in),
        .pl_directed_change_done(pl_directed_change_done),
        .pl_directed_link_auton(pl_directed_link_auton),
        .pl_directed_link_change(pl_directed_link_change),
        .pl_directed_link_speed(pl_directed_link_speed),
        .pl_directed_link_width(pl_directed_link_width),
        .pl_downstream_deemph_source(pl_downstream_deemph_source),
        .pl_initial_link_width(pl_initial_link_width),
        .pl_lane_reversal_mode(pl_lane_reversal_mode),
        .pl_link_gen2_cap(pl_link_gen2_cap),
        .pl_link_partner_gen2_supported(pl_link_partner_gen2_supported),
        .pl_link_upcfg_cap(pl_link_upcfg_cap),
        .pl_ltssm_state(pl_ltssm_state),
        .pl_phy_lnk_up(pl_phy_lnk_up),
        .pl_received_hot_rst(pl_received_hot_rst_wire),
        .pl_rx_pm_state(pl_rx_pm_state),
        .pl_sel_lnk_rate(pl_sel_lnk_rate),
        .pl_sel_lnk_width(pl_sel_lnk_width),
        .pl_transmit_hot_rst(pl_transmit_hot_rst),
        .pl_tx_pm_state(pl_tx_pm_state),
        .pl_upstream_prefer_deemph(pl_upstream_prefer_deemph),
        .rx_np_ok(rx_np_ok),
        .rx_np_req(rx_np_req),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep(s_axis_tx_tkeep),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .src_in(pl_phy_lnk_up_wire),
        .sys_rst_n(gt_top_i_n_0),
        .tready_thrtl_reg(s_axis_tx_tready),
        .trn_lnk_up(trn_lnk_up),
        .trn_tbuf_av(tx_buf_av),
        .trn_tcfg_req(tx_cfg_req),
        .tx_cfg_gnt(tx_cfg_gnt),
        .tx_err_drop(tx_err_drop),
        .user_reset_int_reg(pcie_top_i_n_5));
  (* DEST_SYNC_FF = "2" *) 
  (* INIT_SYNC_FF = "0" *) 
  (* SIM_ASSERT_CHK = "0" *) 
  (* SRC_INPUT_REG = "0" *) 
  (* VERSION = "0" *) 
  (* XPM_CDC = "SINGLE" *) 
  (* XPM_MODULE = "TRUE" *) 
  pcie_7x_bridge_xpm_cdc_single__2 phy_lnk_up_cdc
       (.dest_clk(pipe_userclk2_in),
        .dest_out(pl_phy_lnk_up_sync),
        .src_clk(1'b0),
        .src_in(pl_phy_lnk_up_wire));
  FDRE pl_phy_lnk_up_q_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(pl_phy_lnk_up_sync),
        .Q(pl_phy_lnk_up),
        .R(p_0_in_0));
  (* DEST_SYNC_FF = "2" *) 
  (* INIT_SYNC_FF = "0" *) 
  (* SIM_ASSERT_CHK = "0" *) 
  (* SRC_INPUT_REG = "0" *) 
  (* VERSION = "0" *) 
  (* XPM_CDC = "SINGLE" *) 
  (* XPM_MODULE = "TRUE" *) 
  pcie_7x_bridge_xpm_cdc_single pl_received_hot_rst_cdc
       (.dest_clk(pipe_userclk2_in),
        .dest_out(pl_received_hot_rst_sync),
        .src_clk(1'b0),
        .src_in(pl_received_hot_rst_wire));
  FDRE pl_received_hot_rst_q_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(pl_received_hot_rst_sync),
        .Q(pl_received_hot_rst),
        .R(p_0_in_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  FDRE user_lnk_up_int_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(trn_lnk_up),
        .Q(user_lnk_up_int),
        .R(p_0_in_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  FDRE user_lnk_up_mux_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(user_lnk_up_int),
        .Q(user_lnk_up_mux),
        .R(p_0_in_0));
  FDPE user_reset_int_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(pcie_top_i_n_5),
        .PRE(sys_or_hot_rst),
        .Q(bridge_reset_int));
  LUT2 #(
    .INIT(4'hB)) 
    user_reset_out_i_1
       (.I0(pl_received_hot_rst),
        .I1(sys_rst_n),
        .O(sys_or_hot_rst));
  FDPE user_reset_out_reg
       (.C(pipe_userclk2_in),
        .CE(1'b1),
        .D(bridge_reset_int),
        .PRE(sys_or_hot_rst),
        .Q(user_reset_out));
endmodule

module pcie_7x_bridge_gt_common
   (cpllrst,
    \gtp_common.gtpe2_common_i ,
    \gtp_common.gtpe2_common_i_0 ,
    \gtp_common.gtpe2_common_i_1 ,
    done_reg,
    gt_cpllpdrefclk,
    pipe_dclk_in,
    sys_clk,
    PLL0RESET0,
    SR,
    Q);
  output cpllrst;
  output \gtp_common.gtpe2_common_i ;
  output \gtp_common.gtpe2_common_i_0 ;
  output \gtp_common.gtpe2_common_i_1 ;
  output done_reg;
  input gt_cpllpdrefclk;
  input pipe_dclk_in;
  input sys_clk;
  input PLL0RESET0;
  input [0:0]SR;
  input [0:0]Q;

  wire PLL0RESET0;
  wire [0:0]Q;
  wire [0:0]SR;
  wire cpllrst;
  wire done_reg;
  wire gt_cpllpdrefclk;
  wire \gtp_common.gtpe2_common_i ;
  wire \gtp_common.gtpe2_common_i_0 ;
  wire \gtp_common.gtpe2_common_i_1 ;
  wire pipe_dclk_in;
  wire [7:0]qpll_drp_addr;
  wire [15:0]qpll_drp_di;
  wire [15:0]qpll_drp_do;
  wire qpll_drp_en;
  wire qpll_drp_rdy;
  wire qpll_drp_we;
  wire sys_clk;

  pcie_7x_bridge_qpll_drp qpll_drp_i
       (.D(qpll_drp_do),
        .Q(Q),
        .SR(SR),
        .\addr_reg[7]_0 ({qpll_drp_addr[7],qpll_drp_addr[5],qpll_drp_addr[2:0]}),
        .\di_reg[15]_0 (qpll_drp_di),
        .done_reg_0(done_reg),
        .pipe_dclk_in(pipe_dclk_in),
        .qpll_drp_en(qpll_drp_en),
        .qpll_drp_rdy(qpll_drp_rdy),
        .qpll_drp_we(qpll_drp_we),
        .qplllock_reg1_reg_0(\gtp_common.gtpe2_common_i ));
  pcie_7x_bridge_qpll_wrapper qpll_wrapper_i
       (.D(qpll_drp_do),
        .PLL0RESET0(PLL0RESET0),
        .cpllrst(cpllrst),
        .gt_cpllpdrefclk(gt_cpllpdrefclk),
        .\gtp_common.gtpe2_common_i_0 (\gtp_common.gtpe2_common_i ),
        .\gtp_common.gtpe2_common_i_1 (\gtp_common.gtpe2_common_i_0 ),
        .\gtp_common.gtpe2_common_i_2 (\gtp_common.gtpe2_common_i_1 ),
        .\gtp_common.gtpe2_common_i_3 (qpll_drp_di),
        .\gtp_common.gtpe2_common_i_4 ({qpll_drp_addr[7],qpll_drp_addr[5],qpll_drp_addr[2:0]}),
        .pipe_dclk_in(pipe_dclk_in),
        .qpll_drp_en(qpll_drp_en),
        .qpll_drp_rdy(qpll_drp_rdy),
        .qpll_drp_we(qpll_drp_we),
        .sys_clk(sys_clk));
endmodule

module pcie_7x_bridge_gt_rx_valid_filter_7x
   (pipe_rx0_valid,
    pipe_rx0_elec_idle,
    pipe_rx0_phy_status,
    plm_in_l0__4,
    \reg_state_eios_det_reg[0]_0 ,
    pipe_rx0_data,
    pipe_rx0_char_is_k,
    pipe_rx0_status,
    SR,
    pipe_pclk_in,
    gt_rx_elec_idle_wire_filter,
    gt_rx_phy_status_wire_filter,
    PIPE_RXSTATUS,
    gt_rxvalid_q12_out,
    Q,
    D,
    \gt_rxdata_q_reg[15]_0 );
  output pipe_rx0_valid;
  output pipe_rx0_elec_idle;
  output pipe_rx0_phy_status;
  output plm_in_l0__4;
  output \reg_state_eios_det_reg[0]_0 ;
  output [15:0]pipe_rx0_data;
  output [1:0]pipe_rx0_char_is_k;
  output [2:0]pipe_rx0_status;
  input [0:0]SR;
  input pipe_pclk_in;
  input [0:0]gt_rx_elec_idle_wire_filter;
  input [0:0]gt_rx_phy_status_wire_filter;
  input [2:0]PIPE_RXSTATUS;
  input gt_rxvalid_q12_out;
  input [5:0]Q;
  input [1:0]D;
  input [15:0]\gt_rxdata_q_reg[15]_0 ;

  wire [1:0]D;
  wire [2:0]PIPE_RXSTATUS;
  wire [5:0]Q;
  wire [0:0]SR;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire [0:0]gt_rx_phy_status_wire_filter;
  wire \gt_rx_status_q[0]_i_1_n_0 ;
  wire \gt_rx_status_q[1]_i_1_n_0 ;
  wire \gt_rx_status_q[2]_i_1_n_0 ;
  wire \gt_rxcharisk_q_reg_n_0_[0] ;
  wire [15:0]\gt_rxdata_q_reg[15]_0 ;
  wire gt_rxvalid_q12_out;
  wire gt_rxvalid_q__0;
  wire gt_rxvalid_q_n_0;
  wire p_14_in;
  wire p_1_in;
  wire [4:0]p_1_in__0;
  wire pipe_pclk_in;
  wire [1:0]pipe_rx0_char_is_k;
  wire [15:0]pipe_rx0_data;
  wire pipe_rx0_elec_idle;
  wire pipe_rx0_phy_status;
  wire [2:0]pipe_rx0_status;
  wire pipe_rx0_valid;
  wire plm_in_l0__4;
  wire reg_state_eios_det118_out;
  wire reg_state_eios_det119_out;
  wire reg_state_eios_det1__1;
  wire \reg_state_eios_det[0]_i_2_n_0 ;
  wire \reg_state_eios_det[2]_i_4_n_0 ;
  wire \reg_state_eios_det[2]_i_5_n_0 ;
  wire \reg_state_eios_det[4]_i_1_n_0 ;
  wire \reg_state_eios_det[4]_i_5_n_0 ;
  wire \reg_state_eios_det[4]_i_6_n_0 ;
  wire \reg_state_eios_det_reg[0]_0 ;
  wire reg_symbol_after_eios;
  wire [4:0]state_eios_det;
  wire symbol_after_eios;

  FDRE gt_rx_phy_status_q_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rx_phy_status_wire_filter),
        .Q(pipe_rx0_phy_status),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT3 #(
    .INIT(8'hD0)) 
    \gt_rx_status_q[0]_i_1 
       (.I0(plm_in_l0__4),
        .I1(pipe_rx0_valid),
        .I2(PIPE_RXSTATUS[0]),
        .O(\gt_rx_status_q[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair2" *) 
  LUT3 #(
    .INIT(8'hD0)) 
    \gt_rx_status_q[1]_i_1 
       (.I0(plm_in_l0__4),
        .I1(pipe_rx0_valid),
        .I2(PIPE_RXSTATUS[1]),
        .O(\gt_rx_status_q[1]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT3 #(
    .INIT(8'hD0)) 
    \gt_rx_status_q[2]_i_1 
       (.I0(plm_in_l0__4),
        .I1(pipe_rx0_valid),
        .I2(PIPE_RXSTATUS[2]),
        .O(\gt_rx_status_q[2]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h0000002000000000)) 
    \gt_rx_status_q[2]_i_2 
       (.I0(Q[2]),
        .I1(Q[3]),
        .I2(Q[1]),
        .I3(Q[0]),
        .I4(Q[5]),
        .I5(Q[4]),
        .O(plm_in_l0__4));
  FDRE \gt_rx_status_q_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rx_status_q[0]_i_1_n_0 ),
        .Q(pipe_rx0_status[0]),
        .R(SR));
  FDRE \gt_rx_status_q_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rx_status_q[1]_i_1_n_0 ),
        .Q(pipe_rx0_status[1]),
        .R(SR));
  FDRE \gt_rx_status_q_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rx_status_q[2]_i_1_n_0 ),
        .Q(pipe_rx0_status[2]),
        .R(SR));
  FDRE \gt_rxcharisk_q_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(D[0]),
        .Q(\gt_rxcharisk_q_reg_n_0_[0] ),
        .R(SR));
  FDRE \gt_rxcharisk_q_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(D[1]),
        .Q(p_1_in),
        .R(SR));
  FDRE \gt_rxdata_q_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [0]),
        .Q(pipe_rx0_data[0]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [10]),
        .Q(pipe_rx0_data[10]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [11]),
        .Q(pipe_rx0_data[11]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [12]),
        .Q(pipe_rx0_data[12]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [13]),
        .Q(pipe_rx0_data[13]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [14]),
        .Q(pipe_rx0_data[14]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [15]),
        .Q(pipe_rx0_data[15]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [1]),
        .Q(pipe_rx0_data[1]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [2]),
        .Q(pipe_rx0_data[2]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [3]),
        .Q(pipe_rx0_data[3]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [4]),
        .Q(pipe_rx0_data[4]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [5]),
        .Q(pipe_rx0_data[5]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [6]),
        .Q(pipe_rx0_data[6]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [7]),
        .Q(pipe_rx0_data[7]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [8]),
        .Q(pipe_rx0_data[8]),
        .R(SR));
  FDRE \gt_rxdata_q_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\gt_rxdata_q_reg[15]_0 [9]),
        .Q(pipe_rx0_data[9]),
        .R(SR));
  FDRE gt_rxelecidle_q_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rx_elec_idle_wire_filter),
        .Q(pipe_rx0_elec_idle),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'h00010116)) 
    gt_rxvalid_q
       (.I0(state_eios_det[0]),
        .I1(state_eios_det[1]),
        .I2(state_eios_det[2]),
        .I3(state_eios_det[3]),
        .I4(state_eios_det[4]),
        .O(gt_rxvalid_q_n_0));
  LUT5 #(
    .INIT(32'hFF00FD00)) 
    gt_rxvalid_q_i_1
       (.I0(gt_rxvalid_q_n_0),
        .I1(state_eios_det[0]),
        .I2(state_eios_det[4]),
        .I3(gt_rxvalid_q12_out),
        .I4(\reg_state_eios_det[0]_i_2_n_0 ),
        .O(gt_rxvalid_q__0));
  (* SOFT_HLUTNM = "soft_lutpair1" *) 
  LUT5 #(
    .INIT(32'h00000004)) 
    gt_rxvalid_q_i_4
       (.I0(state_eios_det[0]),
        .I1(state_eios_det[4]),
        .I2(state_eios_det[2]),
        .I3(state_eios_det[3]),
        .I4(state_eios_det[1]),
        .O(\reg_state_eios_det_reg[0]_0 ));
  FDRE gt_rxvalid_q_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rxvalid_q__0),
        .Q(pipe_rx0_valid),
        .R(SR));
  LUT3 #(
    .INIT(8'h08)) 
    pcie_block_i_i_32
       (.I0(pipe_rx0_valid),
        .I1(p_1_in),
        .I2(symbol_after_eios),
        .O(pipe_rx0_char_is_k[1]));
  (* SOFT_HLUTNM = "soft_lutpair3" *) 
  LUT2 #(
    .INIT(4'h8)) 
    pcie_block_i_i_33
       (.I0(pipe_rx0_valid),
        .I1(\gt_rxcharisk_q_reg_n_0_[0] ),
        .O(pipe_rx0_char_is_k[0]));
  LUT5 #(
    .INIT(32'hFFFFAABA)) 
    \reg_state_eios_det[0]_i_1 
       (.I0(state_eios_det[4]),
        .I1(reg_state_eios_det118_out),
        .I2(state_eios_det[0]),
        .I3(reg_state_eios_det119_out),
        .I4(\reg_state_eios_det[0]_i_2_n_0 ),
        .O(p_1_in__0[0]));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT5 #(
    .INIT(32'h50FF5054)) 
    \reg_state_eios_det[0]_i_2 
       (.I0(p_14_in),
        .I1(state_eios_det[1]),
        .I2(state_eios_det[3]),
        .I3(reg_state_eios_det1__1),
        .I4(state_eios_det[2]),
        .O(\reg_state_eios_det[0]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT2 #(
    .INIT(4'h8)) 
    \reg_state_eios_det[1]_i_1 
       (.I0(state_eios_det[0]),
        .I1(reg_state_eios_det119_out),
        .O(p_1_in__0[1]));
  (* SOFT_HLUTNM = "soft_lutpair4" *) 
  LUT3 #(
    .INIT(8'h08)) 
    \reg_state_eios_det[2]_i_1 
       (.I0(state_eios_det[0]),
        .I1(reg_state_eios_det118_out),
        .I2(reg_state_eios_det119_out),
        .O(p_1_in__0[2]));
  LUT6 #(
    .INIT(64'h0000000000002000)) 
    \reg_state_eios_det[2]_i_2 
       (.I0(pipe_rx0_data[15]),
        .I1(pipe_rx0_data[14]),
        .I2(\reg_state_eios_det[2]_i_4_n_0 ),
        .I3(p_1_in),
        .I4(pipe_rx0_data[8]),
        .I5(pipe_rx0_data[9]),
        .O(reg_state_eios_det118_out));
  LUT6 #(
    .INIT(64'h0008000000000000)) 
    \reg_state_eios_det[2]_i_3 
       (.I0(p_1_in),
        .I1(\gt_rxcharisk_q_reg_n_0_[0] ),
        .I2(pipe_rx0_data[1]),
        .I3(pipe_rx0_data[0]),
        .I4(\reg_state_eios_det[2]_i_5_n_0 ),
        .I5(\reg_state_eios_det[4]_i_5_n_0 ),
        .O(reg_state_eios_det119_out));
  LUT4 #(
    .INIT(16'h8000)) 
    \reg_state_eios_det[2]_i_4 
       (.I0(pipe_rx0_data[13]),
        .I1(pipe_rx0_data[12]),
        .I2(pipe_rx0_data[11]),
        .I3(pipe_rx0_data[10]),
        .O(\reg_state_eios_det[2]_i_4_n_0 ));
  LUT5 #(
    .INIT(32'h00000008)) 
    \reg_state_eios_det[2]_i_5 
       (.I0(\reg_state_eios_det[4]_i_6_n_0 ),
        .I1(pipe_rx0_data[7]),
        .I2(pipe_rx0_data[6]),
        .I3(pipe_rx0_data[8]),
        .I4(pipe_rx0_data[9]),
        .O(\reg_state_eios_det[2]_i_5_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \reg_state_eios_det[3]_i_1 
       (.I0(state_eios_det[2]),
        .I1(reg_state_eios_det1__1),
        .O(p_1_in__0[3]));
  LUT5 #(
    .INIT(32'h00010116)) 
    \reg_state_eios_det[4]_i_1 
       (.I0(state_eios_det[1]),
        .I1(state_eios_det[3]),
        .I2(state_eios_det[0]),
        .I3(state_eios_det[4]),
        .I4(state_eios_det[2]),
        .O(\reg_state_eios_det[4]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair0" *) 
  LUT4 #(
    .INIT(16'hECE0)) 
    \reg_state_eios_det[4]_i_2 
       (.I0(reg_state_eios_det1__1),
        .I1(p_14_in),
        .I2(state_eios_det[1]),
        .I3(state_eios_det[3]),
        .O(p_1_in__0[4]));
  LUT5 #(
    .INIT(32'h10000000)) 
    \reg_state_eios_det[4]_i_3 
       (.I0(pipe_rx0_data[9]),
        .I1(pipe_rx0_data[8]),
        .I2(p_1_in),
        .I3(\reg_state_eios_det[4]_i_5_n_0 ),
        .I4(p_14_in),
        .O(reg_state_eios_det1__1));
  LUT6 #(
    .INIT(64'h0000000000002000)) 
    \reg_state_eios_det[4]_i_4 
       (.I0(pipe_rx0_data[6]),
        .I1(pipe_rx0_data[7]),
        .I2(\reg_state_eios_det[4]_i_6_n_0 ),
        .I3(\gt_rxcharisk_q_reg_n_0_[0] ),
        .I4(pipe_rx0_data[0]),
        .I5(pipe_rx0_data[1]),
        .O(p_14_in));
  LUT6 #(
    .INIT(64'h0000800000000000)) 
    \reg_state_eios_det[4]_i_5 
       (.I0(pipe_rx0_data[10]),
        .I1(pipe_rx0_data[11]),
        .I2(pipe_rx0_data[12]),
        .I3(pipe_rx0_data[13]),
        .I4(pipe_rx0_data[15]),
        .I5(pipe_rx0_data[14]),
        .O(\reg_state_eios_det[4]_i_5_n_0 ));
  LUT4 #(
    .INIT(16'h8000)) 
    \reg_state_eios_det[4]_i_6 
       (.I0(pipe_rx0_data[5]),
        .I1(pipe_rx0_data[4]),
        .I2(pipe_rx0_data[3]),
        .I3(pipe_rx0_data[2]),
        .O(\reg_state_eios_det[4]_i_6_n_0 ));
  (* FSM_ENCODED_STATES = "EIOS_DET_NO_STR0:00010,EIOS_DET_STR0:00100,EIOS_DET_STR1:01000,EIOS_DET_IDL:00001,EIOS_DET_DONE:10000" *) 
  FDSE \reg_state_eios_det_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\reg_state_eios_det[4]_i_1_n_0 ),
        .D(p_1_in__0[0]),
        .Q(state_eios_det[0]),
        .S(SR));
  (* FSM_ENCODED_STATES = "EIOS_DET_NO_STR0:00010,EIOS_DET_STR0:00100,EIOS_DET_STR1:01000,EIOS_DET_IDL:00001,EIOS_DET_DONE:10000" *) 
  FDRE \reg_state_eios_det_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\reg_state_eios_det[4]_i_1_n_0 ),
        .D(p_1_in__0[1]),
        .Q(state_eios_det[1]),
        .R(SR));
  (* FSM_ENCODED_STATES = "EIOS_DET_NO_STR0:00010,EIOS_DET_STR0:00100,EIOS_DET_STR1:01000,EIOS_DET_IDL:00001,EIOS_DET_DONE:10000" *) 
  FDRE \reg_state_eios_det_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\reg_state_eios_det[4]_i_1_n_0 ),
        .D(p_1_in__0[2]),
        .Q(state_eios_det[2]),
        .R(SR));
  (* FSM_ENCODED_STATES = "EIOS_DET_NO_STR0:00010,EIOS_DET_STR0:00100,EIOS_DET_STR1:01000,EIOS_DET_IDL:00001,EIOS_DET_DONE:10000" *) 
  FDRE \reg_state_eios_det_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\reg_state_eios_det[4]_i_1_n_0 ),
        .D(p_1_in__0[3]),
        .Q(state_eios_det[3]),
        .R(SR));
  (* FSM_ENCODED_STATES = "EIOS_DET_NO_STR0:00010,EIOS_DET_STR0:00100,EIOS_DET_STR1:01000,EIOS_DET_IDL:00001,EIOS_DET_DONE:10000" *) 
  FDRE \reg_state_eios_det_reg[4] 
       (.C(pipe_pclk_in),
        .CE(\reg_state_eios_det[4]_i_1_n_0 ),
        .D(p_1_in__0[4]),
        .Q(state_eios_det[4]),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000001000000000)) 
    reg_symbol_after_eios_i_1
       (.I0(state_eios_det[4]),
        .I1(state_eios_det[0]),
        .I2(state_eios_det[2]),
        .I3(state_eios_det[3]),
        .I4(state_eios_det[1]),
        .I5(reg_state_eios_det1__1),
        .O(reg_symbol_after_eios));
  FDRE reg_symbol_after_eios_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reg_symbol_after_eios),
        .Q(symbol_after_eios),
        .R(SR));
endmodule

module pcie_7x_bridge_gt_top
   (sys_rst_n,
    p_0_in_0,
    pci_exp_txn,
    pci_exp_txp,
    pipe_rx0_chanisaligned,
    pipe_rxoutclk_out,
    pipe_txoutclk_out,
    pipe_rx0_data,
    pipe_rx0_valid,
    pipe_rx0_elec_idle,
    pipe_rx0_status,
    pipe_rx0_phy_status,
    pipe_pclk_sel_out,
    pipe_rx0_char_is_k,
    reset_n_reg1_reg,
    pipe_pclk_in,
    pipe_dclk_in,
    sys_clk,
    pci_exp_rxn,
    pci_exp_rxp,
    pipe_rx0_polarity,
    pipe_rxusrclk_in,
    pipe_tx_deemph,
    pipe_tx_rcvr_det,
    pipe_tx0_elec_idle,
    pipe_tx0_powerdown,
    pipe_tx_margin,
    pipe_tx0_data,
    pipe_tx0_compliance,
    pipe_tx0_char_is_k,
    pipe_mmcm_lock_in,
    pipe_tx_rate,
    pipe_oobclk_in,
    pl_ltssm_state);
  output sys_rst_n;
  output p_0_in_0;
  output [0:0]pci_exp_txn;
  output [0:0]pci_exp_txp;
  output pipe_rx0_chanisaligned;
  output [0:0]pipe_rxoutclk_out;
  output pipe_txoutclk_out;
  output [15:0]pipe_rx0_data;
  output pipe_rx0_valid;
  output pipe_rx0_elec_idle;
  output [2:0]pipe_rx0_status;
  output pipe_rx0_phy_status;
  output [0:0]pipe_pclk_sel_out;
  output [1:0]pipe_rx0_char_is_k;
  input reset_n_reg1_reg;
  input pipe_pclk_in;
  input pipe_dclk_in;
  input sys_clk;
  input [0:0]pci_exp_rxn;
  input [0:0]pci_exp_rxp;
  input pipe_rx0_polarity;
  input pipe_rxusrclk_in;
  input pipe_tx_deemph;
  input pipe_tx_rcvr_det;
  input pipe_tx0_elec_idle;
  input [1:0]pipe_tx0_powerdown;
  input [2:0]pipe_tx_margin;
  input [15:0]pipe_tx0_data;
  input pipe_tx0_compliance;
  input [1:0]pipe_tx0_char_is_k;
  input pipe_mmcm_lock_in;
  input pipe_tx_rate;
  input pipe_oobclk_in;
  input [5:0]pl_ltssm_state;

  wire [1:0]gt_rx_data_k_wire_filter;
  wire [15:0]gt_rx_data_wire_filter;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire [0:0]gt_rx_phy_status_wire_filter;
  wire \gt_rx_valid_filter[0].GT_RX_VALID_FILTER_7x_inst_n_4 ;
  wire gt_rxvalid_q12_out;
  wire n_0_0;
  wire n_0_1;
  wire p_0_in_0;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire phy_rdy_n;
  wire pipe_dclk_in;
  wire pipe_mmcm_lock_in;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire pipe_rx0_chanisaligned;
  wire [1:0]pipe_rx0_char_is_k;
  wire [15:0]pipe_rx0_data;
  wire pipe_rx0_elec_idle;
  wire pipe_rx0_phy_status;
  wire pipe_rx0_polarity;
  wire [2:0]pipe_rx0_status;
  wire pipe_rx0_valid;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire [1:0]pipe_tx0_char_is_k;
  wire pipe_tx0_compliance;
  wire [15:0]pipe_tx0_data;
  wire pipe_tx0_elec_idle;
  wire [1:0]pipe_tx0_powerdown;
  wire pipe_tx_deemph;
  wire [2:0]pipe_tx_margin;
  wire pipe_tx_rcvr_det;
  wire pipe_txoutclk_out;
  wire pipe_wrapper_i_n_30;
  wire pipe_wrapper_i_n_6;
  wire pipe_wrapper_i_n_7;
  wire pipe_wrapper_i_n_8;
  wire [5:0]pl_ltssm_state;
  wire [5:0]pl_ltssm_state_q;
  wire plm_in_l0__4;
  wire rate_in_reg1_reg0;
  wire rate_reg1_reg0;
  wire reg_clock_locked;
  wire reg_clock_locked_i_1_n_0;
  wire reset_n_reg1_reg;
  wire sys_clk;
  wire sys_rst_n;

  assign rate_in_reg1_reg0 = pipe_tx_rate;
  pcie_7x_bridge_gt_rx_valid_filter_7x \gt_rx_valid_filter[0].GT_RX_VALID_FILTER_7x_inst 
       (.D(gt_rx_data_k_wire_filter),
        .PIPE_RXSTATUS({pipe_wrapper_i_n_6,pipe_wrapper_i_n_7,pipe_wrapper_i_n_8}),
        .Q(pl_ltssm_state_q),
        .SR(phy_rdy_n),
        .gt_rx_elec_idle_wire_filter(gt_rx_elec_idle_wire_filter),
        .gt_rx_phy_status_wire_filter(gt_rx_phy_status_wire_filter),
        .\gt_rxdata_q_reg[15]_0 (gt_rx_data_wire_filter),
        .gt_rxvalid_q12_out(gt_rxvalid_q12_out),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_rx0_char_is_k(pipe_rx0_char_is_k),
        .pipe_rx0_data(pipe_rx0_data),
        .pipe_rx0_elec_idle(pipe_rx0_elec_idle),
        .pipe_rx0_phy_status(pipe_rx0_phy_status),
        .pipe_rx0_status(pipe_rx0_status),
        .pipe_rx0_valid(pipe_rx0_valid),
        .plm_in_l0__4(plm_in_l0__4),
        .\reg_state_eios_det_reg[0]_0 (\gt_rx_valid_filter[0].GT_RX_VALID_FILTER_7x_inst_n_4 ));
  LUT1 #(
    .INIT(2'h2)) 
    i_0
       (.I0(1'b0),
        .O(n_0_0));
  LUT1 #(
    .INIT(2'h2)) 
    i_1
       (.I0(1'b0),
        .O(n_0_1));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_29
       (.I0(phy_rdy_n),
        .O(sys_rst_n));
  FDRE phy_rdy_n_int_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_wrapper_i_n_30),
        .Q(phy_rdy_n),
        .R(1'b0));
  pcie_7x_bridge_pipe_wrapper pipe_wrapper_i
       (.D(gt_rx_data_k_wire_filter),
        .PIPE_RXSTATUS({pipe_wrapper_i_n_6,pipe_wrapper_i_n_7,pipe_wrapper_i_n_8}),
        .gt_rx_elec_idle_wire_filter(gt_rx_elec_idle_wire_filter),
        .gt_rx_phy_status_wire_filter(gt_rx_phy_status_wire_filter),
        .gt_rxvalid_q12_out(gt_rxvalid_q12_out),
        .gt_rxvalid_q_reg(\gt_rx_valid_filter[0].GT_RX_VALID_FILTER_7x_inst_n_4 ),
        .\gtp_channel.gtpe2_channel_i (gt_rx_data_wire_filter),
        .p_0_in_0(p_0_in_0),
        .pci_exp_rxn(pci_exp_rxn),
        .pci_exp_rxp(pci_exp_rxp),
        .pci_exp_txn(pci_exp_txn),
        .pci_exp_txp(pci_exp_txp),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_oobclk_in(pipe_oobclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .pipe_rx0_chanisaligned(pipe_rx0_chanisaligned),
        .pipe_rx0_polarity(pipe_rx0_polarity),
        .pipe_rx0_valid(pipe_rx0_valid),
        .pipe_rxoutclk_out(pipe_rxoutclk_out),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_tx0_char_is_k(pipe_tx0_char_is_k),
        .pipe_tx0_compliance(pipe_tx0_compliance),
        .pipe_tx0_data(pipe_tx0_data),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle),
        .pipe_tx0_powerdown(pipe_tx0_powerdown),
        .pipe_tx_deemph(pipe_tx_deemph),
        .pipe_tx_margin(pipe_tx_margin),
        .pipe_tx_rcvr_det(pipe_tx_rcvr_det),
        .pipe_txoutclk_out(pipe_txoutclk_out),
        .plm_in_l0__4(plm_in_l0__4),
        .\rate_in_reg1_reg[1] ({n_0_1,rate_in_reg1_reg0}),
        .\rate_reg1_reg[1] ({n_0_0,rate_reg1_reg0}),
        .reg_clock_locked(reg_clock_locked),
        .reg_clock_locked_reg(pipe_wrapper_i_n_30),
        .reset_n_reg1_reg_0(reset_n_reg1_reg),
        .sys_clk(sys_clk));
  FDCE \pl_ltssm_state_q_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[0]),
        .Q(pl_ltssm_state_q[0]));
  FDCE \pl_ltssm_state_q_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[1]),
        .Q(pl_ltssm_state_q[1]));
  FDCE \pl_ltssm_state_q_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[2]),
        .Q(pl_ltssm_state_q[2]));
  FDCE \pl_ltssm_state_q_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[3]),
        .Q(pl_ltssm_state_q[3]));
  FDCE \pl_ltssm_state_q_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[4]),
        .Q(pl_ltssm_state_q[4]));
  FDCE \pl_ltssm_state_q_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(pl_ltssm_state[5]),
        .Q(pl_ltssm_state_q[5]));
  LUT1 #(
    .INIT(2'h2)) 
    rate_reg1_reg0_inst
       (.I0(rate_in_reg1_reg0),
        .O(rate_reg1_reg0));
  LUT1 #(
    .INIT(2'h1)) 
    reg_clock_locked_i_1
       (.I0(pipe_mmcm_lock_in),
        .O(reg_clock_locked_i_1_n_0));
  FDCE reg_clock_locked_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(reg_clock_locked_i_1_n_0),
        .D(1'b1),
        .Q(reg_clock_locked));
endmodule

module pcie_7x_bridge_gt_wrapper
   (\gtp_channel.gtpe2_channel_i_0 ,
    pci_exp_txn,
    pci_exp_txp,
    gt_phystatus,
    gt_rxcdrlock,
    pipe_rx0_chanisaligned,
    \gtp_channel.gtpe2_channel_i_1 ,
    gt_rx_elec_idle_wire_filter,
    pipe_rxoutclk_out,
    \gtp_channel.gtpe2_channel_i_2 ,
    \gtp_channel.gtpe2_channel_i_3 ,
    gt_rxratedone,
    gt_rxresetdone,
    \gtp_channel.gtpe2_channel_i_4 ,
    gt_rxvalid,
    \gtp_channel.gtpe2_channel_i_5 ,
    pipe_txoutclk_out,
    \gtp_channel.gtpe2_channel_i_6 ,
    \gtp_channel.gtpe2_channel_i_7 ,
    gt_txratedone,
    gt_txresetdone,
    gt_txsyncdone,
    D,
    PIPE_RXSTATUS,
    \gtp_channel.gtpe2_channel_i_8 ,
    \gtp_channel.gtpe2_channel_i_9 ,
    pipe_dclk_in,
    drp_mux_en,
    \gtp_channel.gtpe2_channel_i_10 ,
    user_eyescanreset,
    pci_exp_rxn,
    pci_exp_rxp,
    rst_gtreset,
    \gtp_channel.gtpe2_channel_i_11 ,
    \gtp_channel.gtpe2_channel_i_12 ,
    user_resetovrd,
    user_rxbufreset,
    user_rxcdrfreqreset,
    user_rxcdrreset,
    user_rxpcsreset,
    user_rxpmareset,
    pipe_rx0_polarity,
    rxsyncallin,
    rst_userrdy,
    pipe_rxusrclk_in,
    user_oobclk,
    pipe_tx_deemph,
    pipe_tx_rcvr_det,
    sync_txdlyen,
    Q,
    pipe_tx0_elec_idle,
    txphaligndone0,
    pipe_pclk_in,
    DRPDI,
    pipe_tx0_powerdown,
    RXRATE,
    pipe_tx_margin,
    pipe_tx0_data,
    pipe_tx0_compliance,
    pipe_tx0_char_is_k,
    TXPOSTCURSOR,
    TXPRECURSOR,
    TXMAINCURSOR,
    DRPADDR);
  output \gtp_channel.gtpe2_channel_i_0 ;
  output [0:0]pci_exp_txn;
  output [0:0]pci_exp_txp;
  output gt_phystatus;
  output gt_rxcdrlock;
  output pipe_rx0_chanisaligned;
  output \gtp_channel.gtpe2_channel_i_1 ;
  output [0:0]gt_rx_elec_idle_wire_filter;
  output [0:0]pipe_rxoutclk_out;
  output \gtp_channel.gtpe2_channel_i_2 ;
  output \gtp_channel.gtpe2_channel_i_3 ;
  output gt_rxratedone;
  output gt_rxresetdone;
  output \gtp_channel.gtpe2_channel_i_4 ;
  output gt_rxvalid;
  output \gtp_channel.gtpe2_channel_i_5 ;
  output pipe_txoutclk_out;
  output \gtp_channel.gtpe2_channel_i_6 ;
  output \gtp_channel.gtpe2_channel_i_7 ;
  output gt_txratedone;
  output gt_txresetdone;
  output gt_txsyncdone;
  output [15:0]D;
  output [2:0]PIPE_RXSTATUS;
  output [15:0]\gtp_channel.gtpe2_channel_i_8 ;
  output [1:0]\gtp_channel.gtpe2_channel_i_9 ;
  input pipe_dclk_in;
  input drp_mux_en;
  input \gtp_channel.gtpe2_channel_i_10 ;
  input user_eyescanreset;
  input [0:0]pci_exp_rxn;
  input [0:0]pci_exp_rxp;
  input rst_gtreset;
  input \gtp_channel.gtpe2_channel_i_11 ;
  input \gtp_channel.gtpe2_channel_i_12 ;
  input user_resetovrd;
  input user_rxbufreset;
  input user_rxcdrfreqreset;
  input user_rxcdrreset;
  input user_rxpcsreset;
  input user_rxpmareset;
  input pipe_rx0_polarity;
  input rxsyncallin;
  input rst_userrdy;
  input pipe_rxusrclk_in;
  input user_oobclk;
  input pipe_tx_deemph;
  input pipe_tx_rcvr_det;
  input sync_txdlyen;
  input [2:0]Q;
  input pipe_tx0_elec_idle;
  input txphaligndone0;
  input pipe_pclk_in;
  input [15:0]DRPDI;
  input [1:0]pipe_tx0_powerdown;
  input [0:0]RXRATE;
  input [2:0]pipe_tx_margin;
  input [15:0]pipe_tx0_data;
  input pipe_tx0_compliance;
  input [1:0]pipe_tx0_char_is_k;
  input [4:0]TXPOSTCURSOR;
  input [4:0]TXPRECURSOR;
  input [6:0]TXMAINCURSOR;
  input [0:0]DRPADDR;

  wire [15:0]D;
  wire [0:0]DRPADDR;
  wire [15:0]DRPDI;
  wire [2:0]PIPE_RXSTATUS;
  wire [2:0]Q;
  wire [0:0]RXRATE;
  wire [6:0]TXMAINCURSOR;
  wire [4:0]TXPOSTCURSOR;
  wire [4:0]TXPRECURSOR;
  wire drp_mux_en;
  wire gt_phystatus;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire gt_rxcdrlock;
  wire gt_rxratedone;
  wire gt_rxresetdone;
  wire gt_rxsyncout;
  wire gt_rxvalid;
  wire gt_txratedone;
  wire gt_txresetdone;
  wire gt_txsyncdone;
  wire gt_txsyncout;
  wire \gtp_channel.gtpe2_channel_i_0 ;
  wire \gtp_channel.gtpe2_channel_i_1 ;
  wire \gtp_channel.gtpe2_channel_i_10 ;
  wire \gtp_channel.gtpe2_channel_i_11 ;
  wire \gtp_channel.gtpe2_channel_i_12 ;
  wire \gtp_channel.gtpe2_channel_i_2 ;
  wire \gtp_channel.gtpe2_channel_i_3 ;
  wire \gtp_channel.gtpe2_channel_i_4 ;
  wire \gtp_channel.gtpe2_channel_i_5 ;
  wire \gtp_channel.gtpe2_channel_i_6 ;
  wire \gtp_channel.gtpe2_channel_i_7 ;
  wire [15:0]\gtp_channel.gtpe2_channel_i_8 ;
  wire [1:0]\gtp_channel.gtpe2_channel_i_9 ;
  wire \gtp_channel.gtpe2_channel_i_n_1 ;
  wire \gtp_channel.gtpe2_channel_i_n_103 ;
  wire \gtp_channel.gtpe2_channel_i_n_104 ;
  wire \gtp_channel.gtpe2_channel_i_n_105 ;
  wire \gtp_channel.gtpe2_channel_i_n_112 ;
  wire \gtp_channel.gtpe2_channel_i_n_113 ;
  wire \gtp_channel.gtpe2_channel_i_n_114 ;
  wire \gtp_channel.gtpe2_channel_i_n_115 ;
  wire \gtp_channel.gtpe2_channel_i_n_116 ;
  wire \gtp_channel.gtpe2_channel_i_n_117 ;
  wire \gtp_channel.gtpe2_channel_i_n_118 ;
  wire \gtp_channel.gtpe2_channel_i_n_119 ;
  wire \gtp_channel.gtpe2_channel_i_n_120 ;
  wire \gtp_channel.gtpe2_channel_i_n_121 ;
  wire \gtp_channel.gtpe2_channel_i_n_122 ;
  wire \gtp_channel.gtpe2_channel_i_n_123 ;
  wire \gtp_channel.gtpe2_channel_i_n_124 ;
  wire \gtp_channel.gtpe2_channel_i_n_125 ;
  wire \gtp_channel.gtpe2_channel_i_n_126 ;
  wire \gtp_channel.gtpe2_channel_i_n_127 ;
  wire \gtp_channel.gtpe2_channel_i_n_14 ;
  wire \gtp_channel.gtpe2_channel_i_n_144 ;
  wire \gtp_channel.gtpe2_channel_i_n_145 ;
  wire \gtp_channel.gtpe2_channel_i_n_146 ;
  wire \gtp_channel.gtpe2_channel_i_n_147 ;
  wire \gtp_channel.gtpe2_channel_i_n_148 ;
  wire \gtp_channel.gtpe2_channel_i_n_149 ;
  wire \gtp_channel.gtpe2_channel_i_n_152 ;
  wire \gtp_channel.gtpe2_channel_i_n_153 ;
  wire \gtp_channel.gtpe2_channel_i_n_154 ;
  wire \gtp_channel.gtpe2_channel_i_n_155 ;
  wire \gtp_channel.gtpe2_channel_i_n_156 ;
  wire \gtp_channel.gtpe2_channel_i_n_157 ;
  wire \gtp_channel.gtpe2_channel_i_n_158 ;
  wire \gtp_channel.gtpe2_channel_i_n_159 ;
  wire \gtp_channel.gtpe2_channel_i_n_160 ;
  wire \gtp_channel.gtpe2_channel_i_n_161 ;
  wire \gtp_channel.gtpe2_channel_i_n_162 ;
  wire \gtp_channel.gtpe2_channel_i_n_163 ;
  wire \gtp_channel.gtpe2_channel_i_n_29 ;
  wire \gtp_channel.gtpe2_channel_i_n_48 ;
  wire \gtp_channel.gtpe2_channel_i_n_49 ;
  wire \gtp_channel.gtpe2_channel_i_n_50 ;
  wire \gtp_channel.gtpe2_channel_i_n_51 ;
  wire \gtp_channel.gtpe2_channel_i_n_52 ;
  wire \gtp_channel.gtpe2_channel_i_n_53 ;
  wire \gtp_channel.gtpe2_channel_i_n_54 ;
  wire \gtp_channel.gtpe2_channel_i_n_55 ;
  wire \gtp_channel.gtpe2_channel_i_n_56 ;
  wire \gtp_channel.gtpe2_channel_i_n_57 ;
  wire \gtp_channel.gtpe2_channel_i_n_58 ;
  wire \gtp_channel.gtpe2_channel_i_n_59 ;
  wire \gtp_channel.gtpe2_channel_i_n_60 ;
  wire \gtp_channel.gtpe2_channel_i_n_61 ;
  wire \gtp_channel.gtpe2_channel_i_n_62 ;
  wire \gtp_channel.gtpe2_channel_i_n_7 ;
  wire \gtp_channel.gtpe2_channel_i_n_8 ;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire pipe_dclk_in;
  wire pipe_pclk_in;
  wire pipe_rx0_chanisaligned;
  wire pipe_rx0_polarity;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire [1:0]pipe_tx0_char_is_k;
  wire pipe_tx0_compliance;
  wire [15:0]pipe_tx0_data;
  wire pipe_tx0_elec_idle;
  wire [1:0]pipe_tx0_powerdown;
  wire pipe_tx_deemph;
  wire [2:0]pipe_tx_margin;
  wire pipe_tx_rcvr_det;
  wire pipe_txoutclk_out;
  wire rst_gtreset;
  wire rst_userrdy;
  wire rxsyncallin;
  wire sync_txdlyen;
  wire txphaligndone0;
  wire user_eyescanreset;
  wire user_oobclk;
  wire user_resetovrd;
  wire user_rxbufreset;
  wire user_rxcdrfreqreset;
  wire user_rxcdrreset;
  wire user_rxpcsreset;
  wire user_rxpmareset;
  wire \NLW_gtp_channel.gtpe2_channel_i_PMARSVDOUT0_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_PMARSVDOUT1_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXCHANBONDSEQ_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXCHANREALIGN_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXCOMINITDET_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXCOMSASDET_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXCOMWAKEDET_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXHEADERVALID_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOSINTDONE_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTARTED_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTROBEDONE_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTROBESTARTED_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOUTCLKFABRIC_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_RXOUTCLKPCS_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_TXCOMFINISH_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_TXGEARBOXREADY_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_TXOUTCLKFABRIC_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_TXOUTCLKPCS_UNCONNECTED ;
  wire \NLW_gtp_channel.gtpe2_channel_i_TXPMARESETDONE_UNCONNECTED ;
  wire [15:0]\NLW_gtp_channel.gtpe2_channel_i_PCSRSVDOUT_UNCONNECTED ;
  wire [1:0]\NLW_gtp_channel.gtpe2_channel_i_RXCLKCORCNT_UNCONNECTED ;
  wire [1:0]\NLW_gtp_channel.gtpe2_channel_i_RXDATAVALID_UNCONNECTED ;
  wire [2:0]\NLW_gtp_channel.gtpe2_channel_i_RXHEADER_UNCONNECTED ;
  wire [4:0]\NLW_gtp_channel.gtpe2_channel_i_RXPHMONITOR_UNCONNECTED ;
  wire [4:0]\NLW_gtp_channel.gtpe2_channel_i_RXPHSLIPMONITOR_UNCONNECTED ;
  wire [1:0]\NLW_gtp_channel.gtpe2_channel_i_RXSTARTOFSEQ_UNCONNECTED ;
  wire [1:0]\NLW_gtp_channel.gtpe2_channel_i_TXBUFSTATUS_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  GTPE2_CHANNEL #(
    .ACJTAG_DEBUG_MODE(1'b0),
    .ACJTAG_MODE(1'b0),
    .ACJTAG_RESET(1'b0),
    .ADAPT_CFG0(20'b00000000000000000000),
    .ALIGN_COMMA_DOUBLE("FALSE"),
    .ALIGN_COMMA_ENABLE(10'b1111111111),
    .ALIGN_COMMA_WORD(1),
    .ALIGN_MCOMMA_DET("TRUE"),
    .ALIGN_MCOMMA_VALUE(10'b1010000011),
    .ALIGN_PCOMMA_DET("TRUE"),
    .ALIGN_PCOMMA_VALUE(10'b0101111100),
    .CBCC_DATA_SOURCE_SEL("DECODED"),
    .CFOK_CFG(43'b1001001000000000000000001000000111010000000),
    .CFOK_CFG2(7'b0100000),
    .CFOK_CFG3(7'b0100000),
    .CFOK_CFG4(1'b0),
    .CFOK_CFG5(2'b00),
    .CFOK_CFG6(4'b0000),
    .CHAN_BOND_KEEP_ALIGN("TRUE"),
    .CHAN_BOND_MAX_SKEW(7),
    .CHAN_BOND_SEQ_1_1(10'b0001001010),
    .CHAN_BOND_SEQ_1_2(10'b0001001010),
    .CHAN_BOND_SEQ_1_3(10'b0001001010),
    .CHAN_BOND_SEQ_1_4(10'b0110111100),
    .CHAN_BOND_SEQ_1_ENABLE(4'b1111),
    .CHAN_BOND_SEQ_2_1(10'b0001000101),
    .CHAN_BOND_SEQ_2_2(10'b0001000101),
    .CHAN_BOND_SEQ_2_3(10'b0001000101),
    .CHAN_BOND_SEQ_2_4(10'b0110111100),
    .CHAN_BOND_SEQ_2_ENABLE(4'b1111),
    .CHAN_BOND_SEQ_2_USE("TRUE"),
    .CHAN_BOND_SEQ_LEN(4),
    .CLK_COMMON_SWING(1'b0),
    .CLK_CORRECT_USE("TRUE"),
    .CLK_COR_KEEP_IDLE("TRUE"),
    .CLK_COR_MAX_LAT(15),
    .CLK_COR_MIN_LAT(13),
    .CLK_COR_PRECEDENCE("TRUE"),
    .CLK_COR_REPEAT_WAIT(0),
    .CLK_COR_SEQ_1_1(10'b0100011100),
    .CLK_COR_SEQ_1_2(10'b0000000000),
    .CLK_COR_SEQ_1_3(10'b0000000000),
    .CLK_COR_SEQ_1_4(10'b0000000000),
    .CLK_COR_SEQ_1_ENABLE(4'b1111),
    .CLK_COR_SEQ_2_1(10'b0000000000),
    .CLK_COR_SEQ_2_2(10'b0000000000),
    .CLK_COR_SEQ_2_3(10'b0000000000),
    .CLK_COR_SEQ_2_4(10'b0000000000),
    .CLK_COR_SEQ_2_ENABLE(4'b0000),
    .CLK_COR_SEQ_2_USE("FALSE"),
    .CLK_COR_SEQ_LEN(1),
    .DEC_MCOMMA_DETECT("TRUE"),
    .DEC_PCOMMA_DETECT("TRUE"),
    .DEC_VALID_COMMA_ONLY("FALSE"),
    .DMONITOR_CFG(24'h000B01),
    .ES_CLK_PHASE_SEL(1'b0),
    .ES_CONTROL(6'b000000),
    .ES_ERRDET_EN("FALSE"),
    .ES_EYE_SCAN_EN("FALSE"),
    .ES_HORZ_OFFSET(12'h010),
    .ES_PMA_CFG(10'b0000000000),
    .ES_PRESCALE(5'b00000),
    .ES_QUALIFIER(80'h00000000000000000000),
    .ES_QUAL_MASK(80'h00000000000000000000),
    .ES_SDATA_MASK(80'h00000000000000000000),
    .ES_VERT_OFFSET(9'b000000000),
    .FTS_DESKEW_SEQ_ENABLE(4'b1111),
    .FTS_LANE_DESKEW_CFG(4'b1111),
    .FTS_LANE_DESKEW_EN("TRUE"),
    .GEARBOX_MODE(3'b000),
    .IS_CLKRSVD0_INVERTED(1'b0),
    .IS_CLKRSVD1_INVERTED(1'b0),
    .IS_DMONITORCLK_INVERTED(1'b0),
    .IS_DRPCLK_INVERTED(1'b0),
    .IS_RXUSRCLK2_INVERTED(1'b0),
    .IS_RXUSRCLK_INVERTED(1'b0),
    .IS_SIGVALIDCLK_INVERTED(1'b0),
    .IS_TXPHDLYTSTCLK_INVERTED(1'b0),
    .IS_TXUSRCLK2_INVERTED(1'b0),
    .IS_TXUSRCLK_INVERTED(1'b0),
    .LOOPBACK_CFG(1'b0),
    .OUTREFCLK_SEL_INV(2'b11),
    .PCS_PCIE_EN("TRUE"),
    .PCS_RSVD_ATTR(48'h000000000100),
    .PD_TRANS_TIME_FROM_P2(12'h03C),
    .PD_TRANS_TIME_NONE_P2(8'h09),
    .PD_TRANS_TIME_TO_P2(8'h64),
    .PMA_LOOPBACK_CFG(1'b0),
    .PMA_RSV(32'h00000333),
    .PMA_RSV2(32'h00002040),
    .PMA_RSV3(2'b00),
    .PMA_RSV4(4'b0000),
    .PMA_RSV5(1'b0),
    .PMA_RSV6(1'b0),
    .PMA_RSV7(1'b0),
    .RXBUFRESET_TIME(5'b00001),
    .RXBUF_ADDR_MODE("FULL"),
    .RXBUF_EIDLE_HI_CNT(4'b0100),
    .RXBUF_EIDLE_LO_CNT(4'b0000),
    .RXBUF_EN("TRUE"),
    .RXBUF_RESET_ON_CB_CHANGE("TRUE"),
    .RXBUF_RESET_ON_COMMAALIGN("FALSE"),
    .RXBUF_RESET_ON_EIDLE("TRUE"),
    .RXBUF_RESET_ON_RATE_CHANGE("TRUE"),
    .RXBUF_THRESH_OVFLW(61),
    .RXBUF_THRESH_OVRD("FALSE"),
    .RXBUF_THRESH_UNDFLW(4),
    .RXCDRFREQRESET_TIME(5'b00001),
    .RXCDRPHRESET_TIME(5'b00001),
    .RXCDR_CFG(83'h0000107FE406001041010),
    .RXCDR_FR_RESET_ON_EIDLE(1'b0),
    .RXCDR_HOLD_DURING_EIDLE(1'b1),
    .RXCDR_LOCK_CFG(6'b010101),
    .RXCDR_PH_RESET_ON_EIDLE(1'b0),
    .RXDLY_CFG(16'h001F),
    .RXDLY_LCFG(9'h030),
    .RXDLY_TAP_CFG(16'h0000),
    .RXGEARBOX_EN("FALSE"),
    .RXISCANRESET_TIME(5'b00001),
    .RXLPMRESET_TIME(7'b0001111),
    .RXLPM_BIAS_STARTUP_DISABLE(1'b0),
    .RXLPM_CFG(4'b0110),
    .RXLPM_CFG1(1'b0),
    .RXLPM_CM_CFG(1'b0),
    .RXLPM_GC_CFG(9'b111100010),
    .RXLPM_GC_CFG2(3'b001),
    .RXLPM_HF_CFG(14'b00001111110000),
    .RXLPM_HF_CFG2(5'b01010),
    .RXLPM_HF_CFG3(4'b0000),
    .RXLPM_HOLD_DURING_EIDLE(1'b1),
    .RXLPM_INCM_CFG(1'b1),
    .RXLPM_IPCM_CFG(1'b0),
    .RXLPM_LF_CFG(18'b000000001111110000),
    .RXLPM_LF_CFG2(5'b01010),
    .RXLPM_OSINT_CFG(3'b100),
    .RXOOB_CFG(7'b0000110),
    .RXOOB_CLK_CFG("FABRIC"),
    .RXOSCALRESET_TIME(5'b00011),
    .RXOSCALRESET_TIMEOUT(5'b00000),
    .RXOUT_DIV(2),
    .RXPCSRESET_TIME(5'b00001),
    .RXPHDLY_CFG(24'h004020),
    .RXPH_CFG(24'h000000),
    .RXPH_MONITOR_SEL(5'b00000),
    .RXPI_CFG0(3'b000),
    .RXPI_CFG1(1'b1),
    .RXPI_CFG2(1'b1),
    .RXPMARESET_TIME(5'b00011),
    .RXPRBS_ERR_LOOPBACK(1'b0),
    .RXSLIDE_AUTO_WAIT(7),
    .RXSLIDE_MODE("PMA"),
    .RXSYNC_MULTILANE(1'b0),
    .RXSYNC_OVRD(1'b1),
    .RXSYNC_SKIP_DA(1'b0),
    .RX_BIAS_CFG(16'b0000111100110011),
    .RX_BUFFER_CFG(6'b000000),
    .RX_CLK25_DIV(4),
    .RX_CLKMUX_EN(1'b1),
    .RX_CM_SEL(2'b11),
    .RX_CM_TRIM(4'b1010),
    .RX_DATA_WIDTH(20),
    .RX_DDI_SEL(6'b000000),
    .RX_DEBUG_CFG(14'b00000000000000),
    .RX_DEFER_RESET_BUF_EN("TRUE"),
    .RX_DISPERR_SEQ_MATCH("TRUE"),
    .RX_OS_CFG(13'b0000010000000),
    .RX_SIG_VALID_DLY(10),
    .RX_XCLK_SEL("RXREC"),
    .SAS_MAX_COM(64),
    .SAS_MIN_COM(36),
    .SATA_BURST_SEQ_LEN(4'b1111),
    .SATA_BURST_VAL(3'b100),
    .SATA_EIDLE_VAL(3'b100),
    .SATA_MAX_BURST(8),
    .SATA_MAX_INIT(21),
    .SATA_MAX_WAKE(7),
    .SATA_MIN_BURST(4),
    .SATA_MIN_INIT(12),
    .SATA_MIN_WAKE(4),
    .SATA_PLL_CFG("VCO_3000MHZ"),
    .SHOW_REALIGN_COMMA("FALSE"),
    .SIM_RECEIVER_DETECT_PASS("TRUE"),
    .SIM_RESET_SPEEDUP("FALSE"),
    .SIM_TX_EIDLE_DRIVE_LEVEL("1"),
    .SIM_VERSION("1.0"),
    .TERM_RCAL_CFG(15'b100001000010000),
    .TERM_RCAL_OVRD(3'b000),
    .TRANS_TIME_RATE(8'h0E),
    .TST_RSV(32'h00000000),
    .TXBUF_EN("FALSE"),
    .TXBUF_RESET_ON_RATE_CHANGE("TRUE"),
    .TXDLY_CFG(16'h001F),
    .TXDLY_LCFG(9'h030),
    .TXDLY_TAP_CFG(16'h0000),
    .TXGEARBOX_EN("FALSE"),
    .TXOOB_CFG(1'b1),
    .TXOUT_DIV(2),
    .TXPCSRESET_TIME(5'b00001),
    .TXPHDLY_CFG(24'h084020),
    .TXPH_CFG(16'h0780),
    .TXPH_MONITOR_SEL(5'b00000),
    .TXPI_CFG0(2'b00),
    .TXPI_CFG1(2'b00),
    .TXPI_CFG2(2'b00),
    .TXPI_CFG3(1'b0),
    .TXPI_CFG4(1'b0),
    .TXPI_CFG5(3'b000),
    .TXPI_GREY_SEL(1'b0),
    .TXPI_INVSTROBE_SEL(1'b0),
    .TXPI_PPMCLK_SEL("TXUSRCLK2"),
    .TXPI_PPM_CFG(8'b00000000),
    .TXPI_SYNFREQ_PPM(3'b000),
    .TXPMARESET_TIME(5'b00011),
    .TXSYNC_MULTILANE(1'b0),
    .TXSYNC_OVRD(1'b1),
    .TXSYNC_SKIP_DA(1'b0),
    .TX_CLK25_DIV(4),
    .TX_CLKMUX_EN(1'b1),
    .TX_DATA_WIDTH(20),
    .TX_DEEMPH0(6'b010100),
    .TX_DEEMPH1(6'b001011),
    .TX_DRIVE_MODE("PIPE"),
    .TX_EIDLE_ASSERT_DELAY(3'b010),
    .TX_EIDLE_DEASSERT_DELAY(3'b010),
    .TX_LOOPBACK_DRIVE_HIZ("FALSE"),
    .TX_MAINCURSOR_SEL(1'b0),
    .TX_MARGIN_FULL_0(7'b1001111),
    .TX_MARGIN_FULL_1(7'b1001110),
    .TX_MARGIN_FULL_2(7'b1001101),
    .TX_MARGIN_FULL_3(7'b1001100),
    .TX_MARGIN_FULL_4(7'b1000011),
    .TX_MARGIN_LOW_0(7'b1000101),
    .TX_MARGIN_LOW_1(7'b1000110),
    .TX_MARGIN_LOW_2(7'b1000011),
    .TX_MARGIN_LOW_3(7'b1000010),
    .TX_MARGIN_LOW_4(7'b1000000),
    .TX_PREDRIVER_MODE(1'b0),
    .TX_RXDETECT_CFG(14'h0064),
    .TX_RXDETECT_REF(3'b011),
    .TX_XCLK_SEL("TXUSR"),
    .UCODEER_CLR(1'b0),
    .USE_PCS_CLK_PHASE_SEL(1'b0)) 
    \gtp_channel.gtpe2_channel_i 
       (.CFGRESET(1'b0),
        .CLKRSVD0(1'b0),
        .CLKRSVD1(1'b0),
        .DMONFIFORESET(1'b0),
        .DMONITORCLK(1'b0),
        .DMONITOROUT({\gtp_channel.gtpe2_channel_i_n_48 ,\gtp_channel.gtpe2_channel_i_n_49 ,\gtp_channel.gtpe2_channel_i_n_50 ,\gtp_channel.gtpe2_channel_i_n_51 ,\gtp_channel.gtpe2_channel_i_n_52 ,\gtp_channel.gtpe2_channel_i_n_53 ,\gtp_channel.gtpe2_channel_i_n_54 ,\gtp_channel.gtpe2_channel_i_n_55 ,\gtp_channel.gtpe2_channel_i_n_56 ,\gtp_channel.gtpe2_channel_i_n_57 ,\gtp_channel.gtpe2_channel_i_n_58 ,\gtp_channel.gtpe2_channel_i_n_59 ,\gtp_channel.gtpe2_channel_i_n_60 ,\gtp_channel.gtpe2_channel_i_n_61 ,\gtp_channel.gtpe2_channel_i_n_62 }),
        .DRPADDR({1'b0,1'b0,1'b0,1'b0,DRPADDR,1'b0,1'b0,1'b0,DRPADDR}),
        .DRPCLK(pipe_dclk_in),
        .DRPDI(DRPDI),
        .DRPDO(D),
        .DRPEN(drp_mux_en),
        .DRPRDY(\gtp_channel.gtpe2_channel_i_0 ),
        .DRPWE(\gtp_channel.gtpe2_channel_i_10 ),
        .EYESCANDATAERROR(\gtp_channel.gtpe2_channel_i_n_1 ),
        .EYESCANMODE(1'b0),
        .EYESCANRESET(user_eyescanreset),
        .EYESCANTRIGGER(1'b0),
        .GTPRXN(pci_exp_rxn),
        .GTPRXP(pci_exp_rxp),
        .GTPTXN(pci_exp_txn),
        .GTPTXP(pci_exp_txp),
        .GTRESETSEL(1'b0),
        .GTRSVD({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .GTRXRESET(rst_gtreset),
        .GTTXRESET(rst_gtreset),
        .LOOPBACK({1'b0,1'b0,1'b0}),
        .PCSRSVDIN({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PCSRSVDOUT(\NLW_gtp_channel.gtpe2_channel_i_PCSRSVDOUT_UNCONNECTED [15:0]),
        .PHYSTATUS(gt_phystatus),
        .PLL0CLK(\gtp_channel.gtpe2_channel_i_11 ),
        .PLL0REFCLK(\gtp_channel.gtpe2_channel_i_12 ),
        .PLL1CLK(1'b0),
        .PLL1REFCLK(1'b0),
        .PMARSVDIN0(1'b0),
        .PMARSVDIN1(1'b0),
        .PMARSVDIN2(1'b0),
        .PMARSVDIN3(1'b0),
        .PMARSVDIN4(1'b0),
        .PMARSVDOUT0(\NLW_gtp_channel.gtpe2_channel_i_PMARSVDOUT0_UNCONNECTED ),
        .PMARSVDOUT1(\NLW_gtp_channel.gtpe2_channel_i_PMARSVDOUT1_UNCONNECTED ),
        .RESETOVRD(user_resetovrd),
        .RX8B10BEN(1'b1),
        .RXADAPTSELTEST({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .RXBUFRESET(user_rxbufreset),
        .RXBUFSTATUS({\gtp_channel.gtpe2_channel_i_n_103 ,\gtp_channel.gtpe2_channel_i_n_104 ,\gtp_channel.gtpe2_channel_i_n_105 }),
        .RXBYTEISALIGNED(\gtp_channel.gtpe2_channel_i_n_7 ),
        .RXBYTEREALIGN(\gtp_channel.gtpe2_channel_i_n_8 ),
        .RXCDRFREQRESET(user_rxcdrfreqreset),
        .RXCDRHOLD(1'b0),
        .RXCDRLOCK(gt_rxcdrlock),
        .RXCDROVRDEN(1'b0),
        .RXCDRRESET(user_rxcdrreset),
        .RXCDRRESETRSV(1'b0),
        .RXCHANBONDSEQ(\NLW_gtp_channel.gtpe2_channel_i_RXCHANBONDSEQ_UNCONNECTED ),
        .RXCHANISALIGNED(pipe_rx0_chanisaligned),
        .RXCHANREALIGN(\NLW_gtp_channel.gtpe2_channel_i_RXCHANREALIGN_UNCONNECTED ),
        .RXCHARISCOMMA({\gtp_channel.gtpe2_channel_i_n_144 ,\gtp_channel.gtpe2_channel_i_n_145 ,\gtp_channel.gtpe2_channel_i_n_146 ,\gtp_channel.gtpe2_channel_i_n_147 }),
        .RXCHARISK({\gtp_channel.gtpe2_channel_i_n_148 ,\gtp_channel.gtpe2_channel_i_n_149 ,\gtp_channel.gtpe2_channel_i_9 }),
        .RXCHBONDEN(1'b0),
        .RXCHBONDI({1'b0,1'b0,1'b0,1'b0}),
        .RXCHBONDLEVEL({1'b0,1'b0,1'b0}),
        .RXCHBONDMASTER(1'b1),
        .RXCHBONDO({\gtp_channel.gtpe2_channel_i_n_152 ,\gtp_channel.gtpe2_channel_i_n_153 ,\gtp_channel.gtpe2_channel_i_n_154 ,\gtp_channel.gtpe2_channel_i_n_155 }),
        .RXCHBONDSLAVE(1'b0),
        .RXCLKCORCNT(\NLW_gtp_channel.gtpe2_channel_i_RXCLKCORCNT_UNCONNECTED [1:0]),
        .RXCOMINITDET(\NLW_gtp_channel.gtpe2_channel_i_RXCOMINITDET_UNCONNECTED ),
        .RXCOMMADET(\gtp_channel.gtpe2_channel_i_n_14 ),
        .RXCOMMADETEN(1'b1),
        .RXCOMSASDET(\NLW_gtp_channel.gtpe2_channel_i_RXCOMSASDET_UNCONNECTED ),
        .RXCOMWAKEDET(\NLW_gtp_channel.gtpe2_channel_i_RXCOMWAKEDET_UNCONNECTED ),
        .RXDATA({\gtp_channel.gtpe2_channel_i_n_112 ,\gtp_channel.gtpe2_channel_i_n_113 ,\gtp_channel.gtpe2_channel_i_n_114 ,\gtp_channel.gtpe2_channel_i_n_115 ,\gtp_channel.gtpe2_channel_i_n_116 ,\gtp_channel.gtpe2_channel_i_n_117 ,\gtp_channel.gtpe2_channel_i_n_118 ,\gtp_channel.gtpe2_channel_i_n_119 ,\gtp_channel.gtpe2_channel_i_n_120 ,\gtp_channel.gtpe2_channel_i_n_121 ,\gtp_channel.gtpe2_channel_i_n_122 ,\gtp_channel.gtpe2_channel_i_n_123 ,\gtp_channel.gtpe2_channel_i_n_124 ,\gtp_channel.gtpe2_channel_i_n_125 ,\gtp_channel.gtpe2_channel_i_n_126 ,\gtp_channel.gtpe2_channel_i_n_127 ,\gtp_channel.gtpe2_channel_i_8 }),
        .RXDATAVALID(\NLW_gtp_channel.gtpe2_channel_i_RXDATAVALID_UNCONNECTED [1:0]),
        .RXDDIEN(1'b0),
        .RXDFEXYDEN(1'b0),
        .RXDISPERR({\gtp_channel.gtpe2_channel_i_n_156 ,\gtp_channel.gtpe2_channel_i_n_157 ,\gtp_channel.gtpe2_channel_i_n_158 ,\gtp_channel.gtpe2_channel_i_n_159 }),
        .RXDLYBYPASS(1'b1),
        .RXDLYEN(1'b0),
        .RXDLYOVRDEN(1'b0),
        .RXDLYSRESET(1'b0),
        .RXDLYSRESETDONE(\gtp_channel.gtpe2_channel_i_1 ),
        .RXELECIDLE(gt_rx_elec_idle_wire_filter),
        .RXELECIDLEMODE({1'b0,1'b0}),
        .RXGEARBOXSLIP(1'b0),
        .RXHEADER(\NLW_gtp_channel.gtpe2_channel_i_RXHEADER_UNCONNECTED [2:0]),
        .RXHEADERVALID(\NLW_gtp_channel.gtpe2_channel_i_RXHEADERVALID_UNCONNECTED ),
        .RXLPMHFHOLD(1'b0),
        .RXLPMHFOVRDEN(1'b0),
        .RXLPMLFHOLD(1'b0),
        .RXLPMLFOVRDEN(1'b0),
        .RXLPMOSINTNTRLEN(1'b0),
        .RXLPMRESET(1'b0),
        .RXMCOMMAALIGNEN(1'b1),
        .RXNOTINTABLE({\gtp_channel.gtpe2_channel_i_n_160 ,\gtp_channel.gtpe2_channel_i_n_161 ,\gtp_channel.gtpe2_channel_i_n_162 ,\gtp_channel.gtpe2_channel_i_n_163 }),
        .RXOOBRESET(1'b0),
        .RXOSCALRESET(1'b0),
        .RXOSHOLD(1'b0),
        .RXOSINTCFG({1'b0,1'b0,1'b1,1'b0}),
        .RXOSINTDONE(\NLW_gtp_channel.gtpe2_channel_i_RXOSINTDONE_UNCONNECTED ),
        .RXOSINTEN(1'b1),
        .RXOSINTHOLD(1'b0),
        .RXOSINTID0({1'b0,1'b0,1'b0,1'b0}),
        .RXOSINTNTRLEN(1'b0),
        .RXOSINTOVRDEN(1'b0),
        .RXOSINTPD(1'b0),
        .RXOSINTSTARTED(\NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTARTED_UNCONNECTED ),
        .RXOSINTSTROBE(1'b0),
        .RXOSINTSTROBEDONE(\NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTROBEDONE_UNCONNECTED ),
        .RXOSINTSTROBESTARTED(\NLW_gtp_channel.gtpe2_channel_i_RXOSINTSTROBESTARTED_UNCONNECTED ),
        .RXOSINTTESTOVRDEN(1'b0),
        .RXOSOVRDEN(1'b0),
        .RXOUTCLK(pipe_rxoutclk_out),
        .RXOUTCLKFABRIC(\NLW_gtp_channel.gtpe2_channel_i_RXOUTCLKFABRIC_UNCONNECTED ),
        .RXOUTCLKPCS(\NLW_gtp_channel.gtpe2_channel_i_RXOUTCLKPCS_UNCONNECTED ),
        .RXOUTCLKSEL({1'b0,1'b0,1'b0}),
        .RXPCOMMAALIGNEN(1'b1),
        .RXPCSRESET(user_rxpcsreset),
        .RXPD(pipe_tx0_powerdown),
        .RXPHALIGN(1'b0),
        .RXPHALIGNDONE(\gtp_channel.gtpe2_channel_i_2 ),
        .RXPHALIGNEN(1'b0),
        .RXPHDLYPD(1'b0),
        .RXPHDLYRESET(1'b0),
        .RXPHMONITOR(\NLW_gtp_channel.gtpe2_channel_i_RXPHMONITOR_UNCONNECTED [4:0]),
        .RXPHOVRDEN(1'b0),
        .RXPHSLIPMONITOR(\NLW_gtp_channel.gtpe2_channel_i_RXPHSLIPMONITOR_UNCONNECTED [4:0]),
        .RXPMARESET(user_rxpmareset),
        .RXPMARESETDONE(\gtp_channel.gtpe2_channel_i_3 ),
        .RXPOLARITY(pipe_rx0_polarity),
        .RXPRBSCNTRESET(1'b0),
        .RXPRBSERR(\gtp_channel.gtpe2_channel_i_n_29 ),
        .RXPRBSSEL({1'b0,1'b0,1'b0}),
        .RXRATE({1'b0,1'b0,RXRATE}),
        .RXRATEDONE(gt_rxratedone),
        .RXRATEMODE(1'b0),
        .RXRESETDONE(gt_rxresetdone),
        .RXSLIDE(1'b0),
        .RXSTARTOFSEQ(\NLW_gtp_channel.gtpe2_channel_i_RXSTARTOFSEQ_UNCONNECTED [1:0]),
        .RXSTATUS(PIPE_RXSTATUS),
        .RXSYNCALLIN(rxsyncallin),
        .RXSYNCDONE(\gtp_channel.gtpe2_channel_i_4 ),
        .RXSYNCIN(gt_rxsyncout),
        .RXSYNCMODE(1'b1),
        .RXSYNCOUT(gt_rxsyncout),
        .RXSYSCLKSEL({1'b0,1'b0}),
        .RXUSERRDY(rst_userrdy),
        .RXUSRCLK(pipe_rxusrclk_in),
        .RXUSRCLK2(pipe_rxusrclk_in),
        .RXVALID(gt_rxvalid),
        .SETERRSTATUS(1'b0),
        .SIGVALIDCLK(user_oobclk),
        .TSTIN({1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1,1'b1}),
        .TX8B10BBYPASS({1'b0,1'b0,1'b0,1'b0}),
        .TX8B10BEN(1'b1),
        .TXBUFDIFFCTRL({1'b1,1'b0,1'b0}),
        .TXBUFSTATUS(\NLW_gtp_channel.gtpe2_channel_i_TXBUFSTATUS_UNCONNECTED [1:0]),
        .TXCHARDISPMODE({1'b0,1'b0,1'b0,pipe_tx0_compliance}),
        .TXCHARDISPVAL({1'b0,1'b0,1'b0,1'b0}),
        .TXCHARISK({1'b0,1'b0,pipe_tx0_char_is_k}),
        .TXCOMFINISH(\NLW_gtp_channel.gtpe2_channel_i_TXCOMFINISH_UNCONNECTED ),
        .TXCOMINIT(1'b0),
        .TXCOMSAS(1'b0),
        .TXCOMWAKE(1'b0),
        .TXDATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,pipe_tx0_data}),
        .TXDEEMPH(pipe_tx_deemph),
        .TXDETECTRX(pipe_tx_rcvr_det),
        .TXDIFFCTRL({1'b1,1'b1,1'b0,1'b0}),
        .TXDIFFPD(1'b0),
        .TXDLYBYPASS(1'b0),
        .TXDLYEN(sync_txdlyen),
        .TXDLYHOLD(1'b0),
        .TXDLYOVRDEN(1'b0),
        .TXDLYSRESET(Q[0]),
        .TXDLYSRESETDONE(\gtp_channel.gtpe2_channel_i_5 ),
        .TXDLYUPDOWN(1'b0),
        .TXELECIDLE(pipe_tx0_elec_idle),
        .TXGEARBOXREADY(\NLW_gtp_channel.gtpe2_channel_i_TXGEARBOXREADY_UNCONNECTED ),
        .TXHEADER({1'b0,1'b0,1'b0}),
        .TXINHIBIT(1'b0),
        .TXMAINCURSOR(TXMAINCURSOR),
        .TXMARGIN(pipe_tx_margin),
        .TXOUTCLK(pipe_txoutclk_out),
        .TXOUTCLKFABRIC(\NLW_gtp_channel.gtpe2_channel_i_TXOUTCLKFABRIC_UNCONNECTED ),
        .TXOUTCLKPCS(\NLW_gtp_channel.gtpe2_channel_i_TXOUTCLKPCS_UNCONNECTED ),
        .TXOUTCLKSEL({1'b0,1'b1,1'b1}),
        .TXPCSRESET(1'b0),
        .TXPD(pipe_tx0_powerdown),
        .TXPDELECIDLEMODE(1'b0),
        .TXPHALIGN(Q[2]),
        .TXPHALIGNDONE(\gtp_channel.gtpe2_channel_i_6 ),
        .TXPHALIGNEN(1'b1),
        .TXPHDLYPD(1'b0),
        .TXPHDLYRESET(1'b0),
        .TXPHDLYTSTCLK(1'b0),
        .TXPHINIT(Q[1]),
        .TXPHINITDONE(\gtp_channel.gtpe2_channel_i_7 ),
        .TXPHOVRDEN(1'b0),
        .TXPIPPMEN(1'b0),
        .TXPIPPMOVRDEN(1'b0),
        .TXPIPPMPD(1'b0),
        .TXPIPPMSEL(1'b0),
        .TXPIPPMSTEPSIZE({1'b0,1'b0,1'b0,1'b0,1'b0}),
        .TXPISOPD(1'b0),
        .TXPMARESET(1'b0),
        .TXPMARESETDONE(\NLW_gtp_channel.gtpe2_channel_i_TXPMARESETDONE_UNCONNECTED ),
        .TXPOLARITY(1'b0),
        .TXPOSTCURSOR(TXPOSTCURSOR),
        .TXPOSTCURSORINV(1'b0),
        .TXPRBSFORCEERR(1'b0),
        .TXPRBSSEL({1'b0,1'b0,1'b0}),
        .TXPRECURSOR(TXPRECURSOR),
        .TXPRECURSORINV(1'b0),
        .TXRATE({1'b0,1'b0,RXRATE}),
        .TXRATEDONE(gt_txratedone),
        .TXRATEMODE(1'b0),
        .TXRESETDONE(gt_txresetdone),
        .TXSEQUENCE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .TXSTARTSEQ(1'b0),
        .TXSWING(1'b0),
        .TXSYNCALLIN(txphaligndone0),
        .TXSYNCDONE(gt_txsyncdone),
        .TXSYNCIN(gt_txsyncout),
        .TXSYNCMODE(1'b1),
        .TXSYNCOUT(gt_txsyncout),
        .TXSYSCLKSEL({1'b0,1'b0}),
        .TXUSERRDY(rst_userrdy),
        .TXUSRCLK(pipe_pclk_in),
        .TXUSRCLK2(pipe_pclk_in));
endmodule

module pcie_7x_bridge_gtp_cpllpd_ovrd
   (cpllpd,
    cpllrst,
    gt_cpllpdrefclk);
  output cpllpd;
  output cpllrst;
  input gt_cpllpdrefclk;

  wire cpllpd;
  wire \cpllpd_wait_reg[31]_srl32_n_1 ;
  wire \cpllpd_wait_reg[63]_srl32_n_1 ;
  wire \cpllpd_wait_reg[94]_srl31_n_0 ;
  wire \cpllreset_wait_reg[126]_srl31_n_0 ;
  wire \cpllreset_wait_reg[31]_srl32_n_1 ;
  wire \cpllreset_wait_reg[63]_srl32_n_1 ;
  wire \cpllreset_wait_reg[95]_srl32_n_1 ;
  wire cpllrst;
  wire gt_cpllpdrefclk;
  wire \NLW_cpllpd_wait_reg[31]_srl32_Q_UNCONNECTED ;
  wire \NLW_cpllpd_wait_reg[63]_srl32_Q_UNCONNECTED ;
  wire \NLW_cpllpd_wait_reg[94]_srl31_Q31_UNCONNECTED ;
  wire \NLW_cpllreset_wait_reg[126]_srl31_Q31_UNCONNECTED ;
  wire \NLW_cpllreset_wait_reg[31]_srl32_Q_UNCONNECTED ;
  wire \NLW_cpllreset_wait_reg[63]_srl32_Q_UNCONNECTED ;
  wire \NLW_cpllreset_wait_reg[95]_srl32_Q_UNCONNECTED ;

  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg[31]_srl32 " *) 
  SRLC32E #(
    .INIT(32'hFFFFFFFF)) 
    \cpllpd_wait_reg[31]_srl32 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(1'b0),
        .Q(\NLW_cpllpd_wait_reg[31]_srl32_Q_UNCONNECTED ),
        .Q31(\cpllpd_wait_reg[31]_srl32_n_1 ));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg[63]_srl32 " *) 
  SRLC32E #(
    .INIT(32'hFFFFFFFF)) 
    \cpllpd_wait_reg[63]_srl32 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(\cpllpd_wait_reg[31]_srl32_n_1 ),
        .Q(\NLW_cpllpd_wait_reg[63]_srl32_Q_UNCONNECTED ),
        .Q31(\cpllpd_wait_reg[63]_srl32_n_1 ));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllpd_wait_reg[94]_srl31 " *) 
  SRLC32E #(
    .INIT(32'h7FFFFFFF)) 
    \cpllpd_wait_reg[94]_srl31 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b0}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(\cpllpd_wait_reg[63]_srl32_n_1 ),
        .Q(\cpllpd_wait_reg[94]_srl31_n_0 ),
        .Q31(\NLW_cpllpd_wait_reg[94]_srl31_Q31_UNCONNECTED ));
  (* equivalent_register_removal = "no" *) 
  FDRE #(
    .INIT(1'b1)) 
    \cpllpd_wait_reg[95] 
       (.C(gt_cpllpdrefclk),
        .CE(1'b1),
        .D(\cpllpd_wait_reg[94]_srl31_n_0 ),
        .Q(cpllpd),
        .R(1'b0));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg[126]_srl31 " *) 
  SRLC32E #(
    .INIT(32'h00000000)) 
    \cpllreset_wait_reg[126]_srl31 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b0}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(\cpllreset_wait_reg[95]_srl32_n_1 ),
        .Q(\cpllreset_wait_reg[126]_srl31_n_0 ),
        .Q31(\NLW_cpllreset_wait_reg[126]_srl31_Q31_UNCONNECTED ));
  (* equivalent_register_removal = "no" *) 
  FDRE #(
    .INIT(1'b0)) 
    \cpllreset_wait_reg[127] 
       (.C(gt_cpllpdrefclk),
        .CE(1'b1),
        .D(\cpllreset_wait_reg[126]_srl31_n_0 ),
        .Q(cpllrst),
        .R(1'b0));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg[31]_srl32 " *) 
  SRLC32E #(
    .INIT(32'h000000FF)) 
    \cpllreset_wait_reg[31]_srl32 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(1'b0),
        .Q(\NLW_cpllreset_wait_reg[31]_srl32_Q_UNCONNECTED ),
        .Q31(\cpllreset_wait_reg[31]_srl32_n_1 ));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg[63]_srl32 " *) 
  SRLC32E #(
    .INIT(32'h00000000)) 
    \cpllreset_wait_reg[63]_srl32 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(\cpllreset_wait_reg[31]_srl32_n_1 ),
        .Q(\NLW_cpllreset_wait_reg[63]_srl32_Q_UNCONNECTED ),
        .Q31(\cpllreset_wait_reg[63]_srl32_n_1 ));
  (* srl_bus_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg " *) 
  (* srl_name = "inst/\\inst/gt_top_i/pipe_wrapper_i/pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i/qpll_wrapper_i/cpllPDInst/cpllreset_wait_reg[95]_srl32 " *) 
  SRLC32E #(
    .INIT(32'h00000000)) 
    \cpllreset_wait_reg[95]_srl32 
       (.A({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .CE(1'b1),
        .CLK(gt_cpllpdrefclk),
        .D(\cpllreset_wait_reg[63]_srl32_n_1 ),
        .Q(\NLW_cpllreset_wait_reg[95]_srl32_Q_UNCONNECTED ),
        .Q31(\cpllreset_wait_reg[95]_srl32_n_1 ));
endmodule

module pcie_7x_bridge_gtp_pipe_drp
   (done,
    \fsm_reg[1]_0 ,
    DRPADDR,
    DRPDI,
    drp_mux_en,
    SR,
    pipe_dclk_in,
    DRP_START0,
    rdy_reg1_reg_0,
    DRP_X160,
    D);
  output done;
  output \fsm_reg[1]_0 ;
  output [0:0]DRPADDR;
  output [15:0]DRPDI;
  output drp_mux_en;
  input [0:0]SR;
  input pipe_dclk_in;
  input DRP_START0;
  input rdy_reg1_reg_0;
  input DRP_X160;
  input [15:0]D;

  wire [15:0]D;
  wire [0:0]DRPADDR;
  wire [15:0]DRPDI;
  wire DRP_START0;
  wire DRP_X160;
  wire [0:0]SR;
  wire [4:4]addr_reg;
  wire \addr_reg_reg_n_0_[4] ;
  wire [15:0]di_reg;
  wire \di_reg[15]_i_1_n_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [15:0]do_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [15:0]do_reg2;
  wire done;
  wire done_i_1_n_0;
  wire drp_mux_en;
  wire [2:0]fsm;
  wire \fsm[0]_i_2_n_0 ;
  wire \fsm_reg[1]_0 ;
  wire \fsm_reg_n_0_[0] ;
  wire \fsm_reg_n_0_[1] ;
  wire \fsm_reg_n_0_[2] ;
  wire \index[4]_i_1_n_0 ;
  wire \index[4]_i_3_n_0 ;
  wire \index_reg_n_0_[0] ;
  wire \index_reg_n_0_[1] ;
  wire \index_reg_n_0_[2] ;
  wire \index_reg_n_0_[3] ;
  wire \index_reg_n_0_[4] ;
  wire load_cnt;
  wire \load_cnt[0]_i_1_n_0 ;
  wire [11:11]p_1_in;
  wire [4:0]p_2_in;
  wire pipe_dclk_in;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rdy_reg1;
  wire rdy_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rdy_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire start_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire start_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire x16_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire x16_reg2;

  LUT5 #(
    .INIT(32'h00000001)) 
    \addr_reg[4]_i_1 
       (.I0(\index_reg_n_0_[0] ),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[3] ),
        .I3(\index_reg_n_0_[2] ),
        .I4(\index_reg_n_0_[4] ),
        .O(addr_reg));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(addr_reg),
        .Q(\addr_reg_reg_n_0_[4] ),
        .R(SR));
  LUT1 #(
    .INIT(2'h1)) 
    \di_reg[11]_i_1 
       (.I0(x16_reg2),
        .O(p_1_in));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFFFE)) 
    \di_reg[15]_i_1 
       (.I0(SR),
        .I1(\index_reg_n_0_[4] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(\index_reg_n_0_[3] ),
        .I4(\index_reg_n_0_[1] ),
        .I5(\index_reg_n_0_[0] ),
        .O(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[0]),
        .Q(di_reg[0]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[10]),
        .Q(di_reg[10]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_1_in),
        .Q(di_reg[11]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[12]),
        .Q(di_reg[12]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[13]),
        .Q(di_reg[13]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[14]),
        .Q(di_reg[14]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[15]),
        .Q(di_reg[15]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[1]),
        .Q(di_reg[1]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[2]),
        .Q(di_reg[2]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[3]),
        .Q(di_reg[3]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[4]),
        .Q(di_reg[4]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[5]),
        .Q(di_reg[5]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[6]),
        .Q(di_reg[6]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[7]),
        .Q(di_reg[7]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[8]),
        .Q(di_reg[8]),
        .R(\di_reg[15]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg2[9]),
        .Q(di_reg[9]),
        .R(\di_reg[15]_i_1_n_0 ));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[0]),
        .Q(do_reg1[0]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[10]),
        .Q(do_reg1[10]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[11]),
        .Q(do_reg1[11]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[12]),
        .Q(do_reg1[12]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[13]),
        .Q(do_reg1[13]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[14]),
        .Q(do_reg1[14]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[15]),
        .Q(do_reg1[15]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[1]),
        .Q(do_reg1[1]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[2]),
        .Q(do_reg1[2]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[3]),
        .Q(do_reg1[3]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[4]),
        .Q(do_reg1[4]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[5]),
        .Q(do_reg1[5]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[6]),
        .Q(do_reg1[6]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[7]),
        .Q(do_reg1[7]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[8]),
        .Q(do_reg1[8]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[9]),
        .Q(do_reg1[9]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[0]),
        .Q(do_reg2[0]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[10]),
        .Q(do_reg2[10]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[11]),
        .Q(do_reg2[11]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[12]),
        .Q(do_reg2[12]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[13]),
        .Q(do_reg2[13]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[14]),
        .Q(do_reg2[14]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[15]),
        .Q(do_reg2[15]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[1]),
        .Q(do_reg2[1]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[2]),
        .Q(do_reg2[2]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[3]),
        .Q(do_reg2[3]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[4]),
        .Q(do_reg2[4]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[5]),
        .Q(do_reg2[5]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[6]),
        .Q(do_reg2[6]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[7]),
        .Q(do_reg2[7]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[8]),
        .Q(do_reg2[8]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[9]),
        .Q(do_reg2[9]),
        .R(SR));
  LUT5 #(
    .INIT(32'hC0C08083)) 
    done_i_1
       (.I0(addr_reg),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[2] ),
        .I3(start_reg2),
        .I4(\fsm_reg_n_0_[0] ),
        .O(done_i_1_n_0));
  FDSE #(
    .INIT(1'b0)) 
    done_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(done_i_1_n_0),
        .Q(done),
        .S(SR));
  LUT6 #(
    .INIT(64'h00000000575F57FF)) 
    \fsm[0]_i_1 
       (.I0(\fsm_reg_n_0_[2] ),
        .I1(addr_reg),
        .I2(\fsm_reg_n_0_[0] ),
        .I3(\fsm_reg_n_0_[1] ),
        .I4(rdy_reg2),
        .I5(\fsm[0]_i_2_n_0 ),
        .O(fsm[0]));
  LUT6 #(
    .INIT(64'h2320000023200303)) 
    \fsm[0]_i_2 
       (.I0(rdy_reg2),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(load_cnt),
        .I4(\fsm_reg_n_0_[0] ),
        .I5(start_reg2),
        .O(\fsm[0]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h50004EAA)) 
    \fsm[1]_i_1 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(load_cnt),
        .I2(rdy_reg2),
        .I3(\fsm_reg_n_0_[0] ),
        .I4(\fsm_reg_n_0_[2] ),
        .O(fsm[1]));
  LUT4 #(
    .INIT(16'h08F0)) 
    \fsm[2]_i_1 
       (.I0(rdy_reg2),
        .I1(\fsm_reg_n_0_[0] ),
        .I2(\fsm_reg_n_0_[2] ),
        .I3(\fsm_reg_n_0_[1] ),
        .O(fsm[2]));
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(fsm[0]),
        .Q(\fsm_reg_n_0_[0] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(fsm[1]),
        .Q(\fsm_reg_n_0_[1] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(fsm[2]),
        .Q(\fsm_reg_n_0_[2] ),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair21" *) 
  LUT3 #(
    .INIT(8'h06)) 
    \gtp_channel.gtpe2_channel_i_i_1 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[0] ),
        .O(drp_mux_en));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_10 
       (.I0(di_reg[11]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[11]));
  (* SOFT_HLUTNM = "soft_lutpair14" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_11 
       (.I0(di_reg[10]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[10]));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_12 
       (.I0(di_reg[9]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[9]));
  (* SOFT_HLUTNM = "soft_lutpair15" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_13 
       (.I0(di_reg[8]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[8]));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_14 
       (.I0(di_reg[7]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[7]));
  (* SOFT_HLUTNM = "soft_lutpair16" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_15 
       (.I0(di_reg[6]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[6]));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_16 
       (.I0(di_reg[5]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[5]));
  (* SOFT_HLUTNM = "soft_lutpair17" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_17 
       (.I0(di_reg[4]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[4]));
  (* SOFT_HLUTNM = "soft_lutpair18" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_18 
       (.I0(di_reg[3]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[3]));
  (* SOFT_HLUTNM = "soft_lutpair18" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_19 
       (.I0(di_reg[2]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[2]));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT3 #(
    .INIT(8'h04)) 
    \gtp_channel.gtpe2_channel_i_i_2 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[0] ),
        .O(\fsm_reg[1]_0 ));
  (* SOFT_HLUTNM = "soft_lutpair19" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_20 
       (.I0(di_reg[1]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[1]));
  (* SOFT_HLUTNM = "soft_lutpair19" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_21 
       (.I0(di_reg[0]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[0]));
  (* SOFT_HLUTNM = "soft_lutpair11" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_39 
       (.I0(\addr_reg_reg_n_0_[4] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPADDR));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_6 
       (.I0(di_reg[15]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[15]));
  (* SOFT_HLUTNM = "soft_lutpair12" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_7 
       (.I0(di_reg[14]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[14]));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_8 
       (.I0(di_reg[13]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[13]));
  (* SOFT_HLUTNM = "soft_lutpair13" *) 
  LUT4 #(
    .INIT(16'hAAA8)) 
    \gtp_channel.gtpe2_channel_i_i_9 
       (.I0(di_reg[12]),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[0] ),
        .O(DRPDI[12]));
  (* SOFT_HLUTNM = "soft_lutpair20" *) 
  LUT4 #(
    .INIT(16'h0004)) 
    \index[0]_i_1 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(addr_reg),
        .I3(\index_reg_n_0_[0] ),
        .O(p_2_in[0]));
  (* SOFT_HLUTNM = "soft_lutpair21" *) 
  LUT4 #(
    .INIT(16'h0600)) 
    \index[1]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\fsm_reg_n_0_[0] ),
        .I3(\fsm_reg_n_0_[2] ),
        .O(p_2_in[1]));
  LUT6 #(
    .INIT(64'h0004040404000000)) 
    \index[2]_i_1 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(addr_reg),
        .I3(\index_reg_n_0_[1] ),
        .I4(\index_reg_n_0_[0] ),
        .I5(\index_reg_n_0_[2] ),
        .O(p_2_in[2]));
  LUT5 #(
    .INIT(32'h2AAA8000)) 
    \index[3]_i_1 
       (.I0(\index[4]_i_3_n_0 ),
        .I1(\index_reg_n_0_[2] ),
        .I2(\index_reg_n_0_[0] ),
        .I3(\index_reg_n_0_[1] ),
        .I4(\index_reg_n_0_[3] ),
        .O(p_2_in[3]));
  LUT3 #(
    .INIT(8'hC1)) 
    \index[4]_i_1 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[2] ),
        .O(\index[4]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h2AAAAAAA80000000)) 
    \index[4]_i_2 
       (.I0(\index[4]_i_3_n_0 ),
        .I1(\index_reg_n_0_[3] ),
        .I2(\index_reg_n_0_[1] ),
        .I3(\index_reg_n_0_[0] ),
        .I4(\index_reg_n_0_[2] ),
        .I5(\index_reg_n_0_[4] ),
        .O(p_2_in[4]));
  (* SOFT_HLUTNM = "soft_lutpair20" *) 
  LUT3 #(
    .INIT(8'h04)) 
    \index[4]_i_3 
       (.I0(addr_reg),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[0] ),
        .O(\index[4]_i_3_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[0] 
       (.C(pipe_dclk_in),
        .CE(\index[4]_i_1_n_0 ),
        .D(p_2_in[0]),
        .Q(\index_reg_n_0_[0] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[1] 
       (.C(pipe_dclk_in),
        .CE(\index[4]_i_1_n_0 ),
        .D(p_2_in[1]),
        .Q(\index_reg_n_0_[1] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[2] 
       (.C(pipe_dclk_in),
        .CE(\index[4]_i_1_n_0 ),
        .D(p_2_in[2]),
        .Q(\index_reg_n_0_[2] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[3] 
       (.C(pipe_dclk_in),
        .CE(\index[4]_i_1_n_0 ),
        .D(p_2_in[3]),
        .Q(\index_reg_n_0_[3] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[4] 
       (.C(pipe_dclk_in),
        .CE(\index[4]_i_1_n_0 ),
        .D(p_2_in[4]),
        .Q(\index_reg_n_0_[4] ),
        .R(SR));
  LUT3 #(
    .INIT(8'h02)) 
    \load_cnt[0]_i_1 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[2] ),
        .O(\load_cnt[0]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \load_cnt_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\load_cnt[0]_i_1_n_0 ),
        .Q(load_cnt),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rdy_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(rdy_reg1_reg_0),
        .Q(rdy_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rdy_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(rdy_reg1),
        .Q(rdy_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE start_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(DRP_START0),
        .Q(start_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE start_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(start_reg1),
        .Q(start_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE x16_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(DRP_X160),
        .Q(x16_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE x16_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(x16_reg1),
        .Q(x16_reg2),
        .R(SR));
endmodule

module pcie_7x_bridge_gtp_pipe_rate
   (pipe_pclk_sel_out,
    DRP_X160,
    DRP_START0,
    Q,
    RXRATE,
    rst_cpllreset,
    done,
    pipe_pclk_in,
    rxpmaresetdone_reg1_reg_0,
    gt_txratedone,
    gt_phystatus,
    gt_rxratedone,
    txsync_done,
    rst_drp_x16,
    rst_drp_start,
    \rate_in_reg1_reg[1]_0 );
  output [0:0]pipe_pclk_sel_out;
  output DRP_X160;
  output DRP_START0;
  output [2:0]Q;
  output [0:0]RXRATE;
  input rst_cpllreset;
  input done;
  input pipe_pclk_in;
  input rxpmaresetdone_reg1_reg_0;
  input gt_txratedone;
  input gt_phystatus;
  input gt_rxratedone;
  input txsync_done;
  input rst_drp_x16;
  input rst_drp_start;
  input [1:0]\rate_in_reg1_reg[1]_0 ;

  wire DRP_START0;
  wire DRP_X160;
  wire \FSM_onehot_fsm[0]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[10]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[11]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[12]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[1]_i_1__1_n_0 ;
  wire \FSM_onehot_fsm[2]_i_1__1_n_0 ;
  wire \FSM_onehot_fsm[3]_i_1_n_0 ;
  wire \FSM_onehot_fsm[4]_i_1__1_n_0 ;
  wire \FSM_onehot_fsm[5]_i_1_n_0 ;
  wire \FSM_onehot_fsm[6]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[7]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[8]_i_1_n_0 ;
  wire \FSM_onehot_fsm[8]_i_2_n_0 ;
  wire \FSM_onehot_fsm[9]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm_reg_n_0_[0] ;
  wire \FSM_onehot_fsm_reg_n_0_[11] ;
  wire \FSM_onehot_fsm_reg_n_0_[12] ;
  wire \FSM_onehot_fsm_reg_n_0_[6] ;
  wire \FSM_onehot_fsm_reg_n_0_[8] ;
  wire [2:0]Q;
  wire [0:0]RXRATE;
  wire done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg2;
  wire gt_phystatus;
  wire gt_rxratedone;
  wire gt_txratedone;
  wire p_0_in1_in;
  wire [3:0]p_0_in__1;
  wire p_2_in;
  wire p_3_in;
  wire pclk_sel;
  wire pclk_sel_i_1_n_0;
  wire phystatus_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire phystatus_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire phystatus_reg2;
  wire phystatus_reg_n_0;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rate_in_reg1;
  wire [1:0]\rate_in_reg1_reg[1]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rate_in_reg2;
  wire rate_out;
  wire \rate_out[0]_i_1_n_0 ;
  wire ratedone_i_1_n_0;
  wire ratedone_i_2_n_0;
  wire ratedone_reg_n_0;
  wire rst_cpllreset;
  wire rst_drp_start;
  wire rst_drp_x16;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxpmaresetdone_reg1;
  wire rxpmaresetdone_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxpmaresetdone_reg2;
  wire rxratedone_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxratedone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxratedone_reg2;
  wire rxratedone_reg_n_0;
  wire [3:0]txdata_wait_cnt_reg;
  wire txratedone_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txratedone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txratedone_reg2;
  wire txratedone_reg_n_0;
  wire txsync_done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_done_reg2;

  LUT3 #(
    .INIT(8'hEA)) 
    \FSM_onehot_fsm[0]_i_1__0 
       (.I0(pclk_sel),
        .I1(drp_done_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[0] ),
        .O(\FSM_onehot_fsm[0]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'h54)) 
    \FSM_onehot_fsm[10]_i_1__0 
       (.I0(drp_done_reg2),
        .I1(p_3_in),
        .I2(p_2_in),
        .O(\FSM_onehot_fsm[10]_i_1__0_n_0 ));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_fsm[11]_i_1__0 
       (.I0(ratedone_reg_n_0),
        .I1(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I2(p_3_in),
        .I3(drp_done_reg2),
        .O(\FSM_onehot_fsm[11]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'hEA)) 
    \FSM_onehot_fsm[12]_i_1__0 
       (.I0(rate_out),
        .I1(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I2(rxpmaresetdone_reg2),
        .O(\FSM_onehot_fsm[12]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'h54)) 
    \FSM_onehot_fsm[1]_i_1__1 
       (.I0(drp_done_reg2),
        .I1(p_0_in1_in),
        .I2(\FSM_onehot_fsm_reg_n_0_[0] ),
        .O(\FSM_onehot_fsm[1]_i_1__1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_fsm[2]_i_1__1 
       (.I0(p_0_in1_in),
        .I1(drp_done_reg2),
        .O(\FSM_onehot_fsm[2]_i_1__1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair24" *) 
  LUT5 #(
    .INIT(32'h80000000)) 
    \FSM_onehot_fsm[3]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I1(txdata_wait_cnt_reg[3]),
        .I2(txdata_wait_cnt_reg[1]),
        .I3(txdata_wait_cnt_reg[0]),
        .I4(txdata_wait_cnt_reg[2]),
        .O(\FSM_onehot_fsm[3]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hEBAAAAEBAAAAAAAA)) 
    \FSM_onehot_fsm[4]_i_1__1 
       (.I0(Q[1]),
        .I1(rate_in_reg1[1]),
        .I2(rate_in_reg2[1]),
        .I3(rate_in_reg1[0]),
        .I4(rate_in_reg2[0]),
        .I5(Q[0]),
        .O(\FSM_onehot_fsm[4]_i_1__1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_fsm[5]_i_1 
       (.I0(txsync_done_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[6] ),
        .O(\FSM_onehot_fsm[5]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'h0E)) 
    \FSM_onehot_fsm[6]_i_1__0 
       (.I0(\FSM_onehot_fsm_reg_n_0_[6] ),
        .I1(Q[2]),
        .I2(txsync_done_reg2),
        .O(\FSM_onehot_fsm[6]_i_1__0_n_0 ));
  LUT4 #(
    .INIT(16'hF888)) 
    \FSM_onehot_fsm[7]_i_1__0 
       (.I0(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I1(ratedone_reg_n_0),
        .I2(txsync_done_reg2),
        .I3(Q[2]),
        .O(\FSM_onehot_fsm[7]_i_1__0_n_0 ));
  LUT6 #(
    .INIT(64'hBEFFFFBEAAAAAAAA)) 
    \FSM_onehot_fsm[8]_i_1 
       (.I0(\FSM_onehot_fsm[8]_i_2_n_0 ),
        .I1(rate_in_reg1[1]),
        .I2(rate_in_reg2[1]),
        .I3(rate_in_reg1[0]),
        .I4(rate_in_reg2[0]),
        .I5(Q[0]),
        .O(\FSM_onehot_fsm[8]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair22" *) 
  LUT5 #(
    .INIT(32'h2AAAAAAA)) 
    \FSM_onehot_fsm[8]_i_2 
       (.I0(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I1(txdata_wait_cnt_reg[3]),
        .I2(txdata_wait_cnt_reg[1]),
        .I3(txdata_wait_cnt_reg[0]),
        .I4(txdata_wait_cnt_reg[2]),
        .O(\FSM_onehot_fsm[8]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_fsm[9]_i_1__0 
       (.I0(rxpmaresetdone_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I2(drp_done_reg2),
        .I3(p_2_in),
        .O(\FSM_onehot_fsm[9]_i_1__0_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[0]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[0] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[10]_i_1__0_n_0 ),
        .Q(p_3_in),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[11]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[11] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[12]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[12] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[1]_i_1__1_n_0 ),
        .Q(p_0_in1_in),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[2]_i_1__1_n_0 ),
        .Q(rate_out),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[3]_i_1_n_0 ),
        .Q(pclk_sel),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDSE #(
    .INIT(1'b1)) 
    \FSM_onehot_fsm_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[4]_i_1__1_n_0 ),
        .Q(Q[0]),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[5]_i_1_n_0 ),
        .Q(Q[1]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[6]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[6] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[7]_i_1__0_n_0 ),
        .Q(Q[2]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[8]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[8] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_DRP_X16_DONE:0000000000010,FSM_DRP_X16_START:0000000000001,FSM_PCLK_SEL:0000000001000,FSM_TXSYNC_DONE:0000001000000,FSM_DONE:0000000100000,FSM_TXSYNC_START:0000010000000,FSM_TXDATA_WAIT:0000100000000,FSM_IDLE:0000000010000,FSM_RATE_DONE:0100000000000,FSM_DRP_X20_START:0001000000000,FSM_DRP_X20_DONE:0010000000000,FSM_RXPMARESETDONE:1000000000000,FSM_RATE_SEL:0000000000100" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[9]_i_1__0_n_0 ),
        .Q(p_2_in),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE drp_done_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(done),
        .Q(drp_done_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE drp_done_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(drp_done_reg1),
        .Q(drp_done_reg2),
        .R(rst_cpllreset));
  LUT4 #(
    .INIT(16'h2F20)) 
    pclk_sel_i_1
       (.I0(rate_in_reg2[0]),
        .I1(rate_in_reg2[1]),
        .I2(pclk_sel),
        .I3(pipe_pclk_sel_out),
        .O(pclk_sel_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    pclk_sel_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pclk_sel_i_1_n_0),
        .Q(pipe_pclk_sel_out),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'hFFFFFFFCAAAAAAA8)) 
    phystatus_i_1
       (.I0(phystatus_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I3(p_2_in),
        .I4(p_3_in),
        .I5(phystatus_reg_n_0),
        .O(phystatus_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    phystatus_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(phystatus_i_1_n_0),
        .Q(phystatus_reg_n_0),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE phystatus_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_phystatus),
        .Q(phystatus_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE phystatus_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(phystatus_reg1),
        .Q(phystatus_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_in_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rate_in_reg1_reg[1]_0 [0]),
        .Q(rate_in_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_in_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rate_in_reg1_reg[1]_0 [1]),
        .Q(rate_in_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_in_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_in_reg1[0]),
        .Q(rate_in_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_in_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_in_reg1[1]),
        .Q(rate_in_reg2[1]),
        .R(rst_cpllreset));
  LUT4 #(
    .INIT(16'h2F20)) 
    \rate_out[0]_i_1 
       (.I0(rate_in_reg2[0]),
        .I1(rate_in_reg2[1]),
        .I2(rate_out),
        .I3(RXRATE),
        .O(\rate_out[0]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \rate_out_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rate_out[0]_i_1_n_0 ),
        .Q(RXRATE),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'h55554000)) 
    ratedone_i_1
       (.I0(ratedone_i_2_n_0),
        .I1(txratedone_reg_n_0),
        .I2(phystatus_reg_n_0),
        .I3(rxratedone_reg_n_0),
        .I4(ratedone_reg_n_0),
        .O(ratedone_i_1_n_0));
  LUT4 #(
    .INIT(16'h0001)) 
    ratedone_i_2
       (.I0(p_3_in),
        .I1(p_2_in),
        .I2(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I3(\FSM_onehot_fsm_reg_n_0_[12] ),
        .O(ratedone_i_2_n_0));
  FDRE #(
    .INIT(1'b0)) 
    ratedone_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(ratedone_i_1_n_0),
        .Q(ratedone_reg_n_0),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxpmaresetdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxpmaresetdone_reg1_reg_0),
        .Q(rxpmaresetdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxpmaresetdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxpmaresetdone_reg1),
        .Q(rxpmaresetdone_reg2),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'hFFFFFFFCAAAAAAA8)) 
    rxratedone_i_1
       (.I0(rxratedone_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I3(p_2_in),
        .I4(p_3_in),
        .I5(rxratedone_reg_n_0),
        .O(rxratedone_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    rxratedone_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxratedone_i_1_n_0),
        .Q(rxratedone_reg_n_0),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxratedone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rxratedone),
        .Q(rxratedone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxratedone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxratedone_reg1),
        .Q(rxratedone_reg2),
        .R(rst_cpllreset));
  (* SOFT_HLUTNM = "soft_lutpair25" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    start_reg1_i_1
       (.I0(rst_drp_start),
        .I1(\FSM_onehot_fsm_reg_n_0_[0] ),
        .I2(p_2_in),
        .O(DRP_START0));
  (* SOFT_HLUTNM = "soft_lutpair23" *) 
  LUT5 #(
    .INIT(32'h8A0A0A0A)) 
    \txdata_wait_cnt[0]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I1(txdata_wait_cnt_reg[2]),
        .I2(txdata_wait_cnt_reg[0]),
        .I3(txdata_wait_cnt_reg[1]),
        .I4(txdata_wait_cnt_reg[3]),
        .O(p_0_in__1[0]));
  (* SOFT_HLUTNM = "soft_lutpair23" *) 
  LUT5 #(
    .INIT(32'hA8282828)) 
    \txdata_wait_cnt[1]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I1(txdata_wait_cnt_reg[0]),
        .I2(txdata_wait_cnt_reg[1]),
        .I3(txdata_wait_cnt_reg[2]),
        .I4(txdata_wait_cnt_reg[3]),
        .O(p_0_in__1[1]));
  (* SOFT_HLUTNM = "soft_lutpair22" *) 
  LUT5 #(
    .INIT(32'hEA006A00)) 
    \txdata_wait_cnt[2]_i_1 
       (.I0(txdata_wait_cnt_reg[2]),
        .I1(txdata_wait_cnt_reg[1]),
        .I2(txdata_wait_cnt_reg[0]),
        .I3(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I4(txdata_wait_cnt_reg[3]),
        .O(p_0_in__1[2]));
  (* SOFT_HLUTNM = "soft_lutpair24" *) 
  LUT5 #(
    .INIT(32'hA8888888)) 
    \txdata_wait_cnt[3]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I1(txdata_wait_cnt_reg[3]),
        .I2(txdata_wait_cnt_reg[1]),
        .I3(txdata_wait_cnt_reg[0]),
        .I4(txdata_wait_cnt_reg[2]),
        .O(p_0_in__1[3]));
  FDRE #(
    .INIT(1'b0)) 
    \txdata_wait_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__1[0]),
        .Q(txdata_wait_cnt_reg[0]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txdata_wait_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__1[1]),
        .Q(txdata_wait_cnt_reg[1]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txdata_wait_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__1[2]),
        .Q(txdata_wait_cnt_reg[2]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txdata_wait_cnt_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__1[3]),
        .Q(txdata_wait_cnt_reg[3]),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'hFFFFFFFCAAAAAAA8)) 
    txratedone_i_1
       (.I0(txratedone_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[11] ),
        .I3(p_2_in),
        .I4(p_3_in),
        .I5(txratedone_reg_n_0),
        .O(txratedone_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    txratedone_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txratedone_i_1_n_0),
        .Q(txratedone_reg_n_0),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txratedone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_txratedone),
        .Q(txratedone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txratedone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txratedone_reg1),
        .Q(txratedone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsync_done_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_done),
        .Q(txsync_done_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsync_done_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_done_reg1),
        .Q(txsync_done_reg2),
        .R(rst_cpllreset));
  (* SOFT_HLUTNM = "soft_lutpair25" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    x16_reg1_i_1
       (.I0(rst_drp_x16),
        .I1(p_0_in1_in),
        .I2(\FSM_onehot_fsm_reg_n_0_[0] ),
        .O(DRP_X160));
endmodule

module pcie_7x_bridge_gtp_pipe_reset
   (reset_n_reg2_reg,
    SR,
    rst_drp_start,
    rst_drp_x16,
    rst_cpllreset,
    rst_gtreset,
    rst_userrdy,
    rxusrclk_rst_reg2_reg_0,
    PLL0RESET0,
    SYNC_TXSYNC_START0,
    \FSM_onehot_fsm_reg[1]_0 ,
    pipe_mmcm_lock_in,
    pipe_pclk_in,
    plllock_reg1_reg_0,
    user_resetdone,
    pipe_dclk_in,
    done,
    \rxpmaresetdone_reg1_reg[0]_0 ,
    gt_phystatus,
    txsync_done,
    Q,
    user_rxcdrlock,
    pipe_rxusrclk_in,
    cpllrst,
    out);
  output reset_n_reg2_reg;
  output [0:0]SR;
  output rst_drp_start;
  output rst_drp_x16;
  output rst_cpllreset;
  output rst_gtreset;
  output rst_userrdy;
  output [0:0]rxusrclk_rst_reg2_reg_0;
  output PLL0RESET0;
  output SYNC_TXSYNC_START0;
  output [0:0]\FSM_onehot_fsm_reg[1]_0 ;
  input pipe_mmcm_lock_in;
  input pipe_pclk_in;
  input plllock_reg1_reg_0;
  input user_resetdone;
  input pipe_dclk_in;
  input done;
  input \rxpmaresetdone_reg1_reg[0]_0 ;
  input gt_phystatus;
  input txsync_done;
  input [1:0]Q;
  input user_rxcdrlock;
  input pipe_rxusrclk_in;
  input cpllrst;
  input out;

  wire \FSM_onehot_fsm[0]_i_1_n_0 ;
  wire \FSM_onehot_fsm[10]_i_1_n_0 ;
  wire \FSM_onehot_fsm[11]_i_1_n_0 ;
  wire \FSM_onehot_fsm[12]_i_1_n_0 ;
  wire \FSM_onehot_fsm[12]_i_2_n_0 ;
  wire \FSM_onehot_fsm[13]_i_1_n_0 ;
  wire \FSM_onehot_fsm[14]_i_2_n_0 ;
  wire \FSM_onehot_fsm[1]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[2]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[3]_i_1__1_n_0 ;
  wire \FSM_onehot_fsm[4]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[5]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[6]_i_1_n_0 ;
  wire \FSM_onehot_fsm[7]_i_1_n_0 ;
  wire \FSM_onehot_fsm[8]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[9]_i_1_n_0 ;
  wire [0:0]\FSM_onehot_fsm_reg[1]_0 ;
  wire \FSM_onehot_fsm_reg_n_0_[10] ;
  wire \FSM_onehot_fsm_reg_n_0_[12] ;
  wire \FSM_onehot_fsm_reg_n_0_[13] ;
  wire \FSM_onehot_fsm_reg_n_0_[2] ;
  wire \FSM_onehot_fsm_reg_n_0_[3] ;
  wire \FSM_onehot_fsm_reg_n_0_[5] ;
  wire \FSM_onehot_fsm_reg_n_0_[6] ;
  wire \FSM_onehot_fsm_reg_n_0_[7] ;
  wire \FSM_onehot_fsm_reg_n_0_[8] ;
  wire \FSM_onehot_fsm_reg_n_0_[9] ;
  wire PLL0RESET0;
  wire [1:0]Q;
  wire RST_DRP_START0;
  wire RST_DRP_X160;
  wire [0:0]SR;
  wire SYNC_TXSYNC_START0;
  wire \cfg_wait_cnt[5]_i_2_n_0 ;
  wire [5:0]cfg_wait_cnt_reg;
  wire cpllrst;
  wire dclk_rst_reg1;
  wire dclk_rst_reg1_0;
  wire done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg2;
  wire gt_phystatus;
  wire gtreset_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg2;
  wire out;
  wire p_0_in0_in;
  wire [5:0]p_0_in__0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire phystatus_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire phystatus_reg2;
  wire pipe_dclk_in;
  wire pipe_mmcm_lock_in;
  wire pipe_pclk_in;
  wire pipe_rxusrclk_in;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire plllock_reg1;
  wire plllock_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire plllock_reg2;
  wire pllreset_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg2;
  wire reset_n_reg2_reg;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire resetdone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire resetdone_reg2;
  wire rst_cpllreset;
  wire rst_drp_start;
  wire rst_drp_x16;
  wire rst_gtreset;
  wire rst_txsync_start;
  wire rst_userrdy;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxpmaresetdone_reg1;
  wire \rxpmaresetdone_reg1_reg[0]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxpmaresetdone_reg2;
  wire rxusrclk_rst_reg1;
  wire rxusrclk_rst_reg2_i_1_n_0;
  wire [0:0]rxusrclk_rst_reg2_reg_0;
  wire txsync_done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_done_reg2;
  wire user_resetdone;
  wire user_rxcdrlock;
  wire userrdy;
  wire userrdy_i_1_n_0;

  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_fsm[0]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .O(\FSM_onehot_fsm[0]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'h54)) 
    \FSM_onehot_fsm[10]_i_1 
       (.I0(drp_done_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[10] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[9] ),
        .O(\FSM_onehot_fsm[10]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFF202020)) 
    \FSM_onehot_fsm[11]_i_1 
       (.I0(resetdone_reg2),
        .I1(phystatus_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[13] ),
        .I3(txsync_done_reg2),
        .I4(rst_txsync_start),
        .O(\FSM_onehot_fsm[11]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFFF44444)) 
    \FSM_onehot_fsm[12]_i_1 
       (.I0(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .I1(dclk_rst_reg1_0),
        .I2(plllock_reg2),
        .I3(resetdone_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[12] ),
        .O(\FSM_onehot_fsm[12]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h7FFFFFFFFFFFFFFF)) 
    \FSM_onehot_fsm[12]_i_2 
       (.I0(cfg_wait_cnt_reg[4]),
        .I1(cfg_wait_cnt_reg[3]),
        .I2(cfg_wait_cnt_reg[5]),
        .I3(cfg_wait_cnt_reg[0]),
        .I4(cfg_wait_cnt_reg[1]),
        .I5(cfg_wait_cnt_reg[2]),
        .O(\FSM_onehot_fsm[12]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hFF8F8888)) 
    \FSM_onehot_fsm[13]_i_1 
       (.I0(userrdy),
        .I1(mmcm_lock_reg2),
        .I2(resetdone_reg2),
        .I3(phystatus_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[13] ),
        .O(\FSM_onehot_fsm[13]_i_1_n_0 ));
  LUT1 #(
    .INIT(2'h1)) 
    \FSM_onehot_fsm[14]_i_1 
       (.I0(out),
        .O(reset_n_reg2_reg));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_fsm[14]_i_2 
       (.I0(mmcm_lock_reg2),
        .I1(userrdy),
        .I2(\FSM_onehot_fsm_reg_n_0_[5] ),
        .I3(drp_done_reg2),
        .O(\FSM_onehot_fsm[14]_i_2_n_0 ));
  LUT3 #(
    .INIT(8'hEA)) 
    \FSM_onehot_fsm[1]_i_1__0 
       (.I0(\FSM_onehot_fsm_reg[1]_0 ),
        .I1(\FSM_onehot_fsm_reg_n_0_[7] ),
        .I2(txsync_done_reg2),
        .O(\FSM_onehot_fsm[1]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'hBA)) 
    \FSM_onehot_fsm[2]_i_1__0 
       (.I0(\FSM_onehot_fsm_reg_n_0_[6] ),
        .I1(rxpmaresetdone_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[2] ),
        .O(\FSM_onehot_fsm[2]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'hA8)) 
    \FSM_onehot_fsm[3]_i_1__1 
       (.I0(rxpmaresetdone_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[2] ),
        .O(\FSM_onehot_fsm[3]_i_1__1_n_0 ));
  LUT4 #(
    .INIT(16'h8F88)) 
    \FSM_onehot_fsm[4]_i_1__0 
       (.I0(drp_done_reg2),
        .I1(p_0_in0_in),
        .I2(rxpmaresetdone_reg2),
        .I3(\FSM_onehot_fsm_reg_n_0_[3] ),
        .O(\FSM_onehot_fsm[4]_i_1__0_n_0 ));
  LUT3 #(
    .INIT(8'h54)) 
    \FSM_onehot_fsm[5]_i_1__0 
       (.I0(drp_done_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[5] ),
        .I2(p_0_in0_in),
        .O(\FSM_onehot_fsm[5]_i_1__0_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_fsm[6]_i_1 
       (.I0(plllock_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[8] ),
        .O(\FSM_onehot_fsm[6]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'h0E)) 
    \FSM_onehot_fsm[7]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[7] ),
        .I1(rst_txsync_start),
        .I2(txsync_done_reg2),
        .O(\FSM_onehot_fsm[7]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'h8F88)) 
    \FSM_onehot_fsm[8]_i_1__0 
       (.I0(drp_done_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[10] ),
        .I2(plllock_reg2),
        .I3(\FSM_onehot_fsm_reg_n_0_[8] ),
        .O(\FSM_onehot_fsm[8]_i_1__0_n_0 ));
  LUT5 #(
    .INIT(32'hFF101010)) 
    \FSM_onehot_fsm[9]_i_1 
       (.I0(plllock_reg2),
        .I1(resetdone_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I3(drp_done_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[9] ),
        .O(\FSM_onehot_fsm[9]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDSE #(
    .INIT(1'b1)) 
    \FSM_onehot_fsm_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[0]_i_1_n_0 ),
        .Q(dclk_rst_reg1_0),
        .S(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[10]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[10] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[11]_i_1_n_0 ),
        .Q(rst_txsync_start),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[12]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[12] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[13]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[13] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[14]_i_2_n_0 ),
        .Q(userrdy),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[1]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg[1]_0 ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[2]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[2] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[3]_i_1__1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[3] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[4]_i_1__0_n_0 ),
        .Q(p_0_in0_in),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[5]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[5] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[6]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[6] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[7]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[7] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[8]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[8] ),
        .R(reset_n_reg2_reg));
  (* FSM_ENCODED_STATES = "FSM_IDLE:000000000000010,FSM_DRP_X20_START:000000000010000,FSM_RXPMARESETDONE_1:000000000000100,FSM_RXPMARESETDONE_2:000000000001000,FSM_GTRESET:000000001000000,FSM_TXSYNC_DONE:000000010000000,FSM_PLLLOCK:000000100000000,FSM_DRP_X16_START:000001000000000,FSM_DRP_X16_DONE:000010000000000,FSM_TXSYNC_START:000100000000000,FSM_PLLRESET:001000000000000,FSM_MMCM_LOCK:100000000000000,FSM_RESETDONE:010000000000000,FSM_DRP_X20_DONE:000000000100000,FSM_CFG_WAIT:000000000000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[9]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[9] ),
        .R(reset_n_reg2_reg));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT2 #(
    .INIT(4'hE)) 
    RST_DRP_START_i_1
       (.I0(p_0_in0_in),
        .I1(\FSM_onehot_fsm_reg_n_0_[9] ),
        .O(RST_DRP_START0));
  FDRE RST_DRP_START_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(RST_DRP_START0),
        .Q(rst_drp_start),
        .R(reset_n_reg2_reg));
  (* SOFT_HLUTNM = "soft_lutpair10" *) 
  LUT2 #(
    .INIT(4'hE)) 
    RST_DRP_X16_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[10] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[9] ),
        .O(RST_DRP_X160));
  FDRE RST_DRP_X16_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(RST_DRP_X160),
        .Q(rst_drp_x16),
        .R(reset_n_reg2_reg));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT3 #(
    .INIT(8'h2A)) 
    \cfg_wait_cnt[0]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .I2(cfg_wait_cnt_reg[0]),
        .O(p_0_in__0[0]));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT4 #(
    .INIT(16'h28AA)) 
    \cfg_wait_cnt[1]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(cfg_wait_cnt_reg[0]),
        .I2(cfg_wait_cnt_reg[1]),
        .I3(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .O(p_0_in__0[1]));
  (* SOFT_HLUTNM = "soft_lutpair5" *) 
  LUT5 #(
    .INIT(32'h2888AAAA)) 
    \cfg_wait_cnt[2]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(cfg_wait_cnt_reg[2]),
        .I2(cfg_wait_cnt_reg[1]),
        .I3(cfg_wait_cnt_reg[0]),
        .I4(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .O(p_0_in__0[2]));
  LUT6 #(
    .INIT(64'h28888888AAAAAAAA)) 
    \cfg_wait_cnt[3]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(cfg_wait_cnt_reg[3]),
        .I2(cfg_wait_cnt_reg[0]),
        .I3(cfg_wait_cnt_reg[1]),
        .I4(cfg_wait_cnt_reg[2]),
        .I5(\FSM_onehot_fsm[12]_i_2_n_0 ),
        .O(p_0_in__0[3]));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT5 #(
    .INIT(32'hEA006A00)) 
    \cfg_wait_cnt[4]_i_1 
       (.I0(cfg_wait_cnt_reg[4]),
        .I1(\cfg_wait_cnt[5]_i_2_n_0 ),
        .I2(cfg_wait_cnt_reg[3]),
        .I3(dclk_rst_reg1_0),
        .I4(cfg_wait_cnt_reg[5]),
        .O(p_0_in__0[4]));
  (* SOFT_HLUTNM = "soft_lutpair6" *) 
  LUT5 #(
    .INIT(32'hA8888888)) 
    \cfg_wait_cnt[5]_i_1 
       (.I0(dclk_rst_reg1_0),
        .I1(cfg_wait_cnt_reg[5]),
        .I2(\cfg_wait_cnt[5]_i_2_n_0 ),
        .I3(cfg_wait_cnt_reg[3]),
        .I4(cfg_wait_cnt_reg[4]),
        .O(p_0_in__0[5]));
  (* SOFT_HLUTNM = "soft_lutpair7" *) 
  LUT3 #(
    .INIT(8'h80)) 
    \cfg_wait_cnt[5]_i_2 
       (.I0(cfg_wait_cnt_reg[2]),
        .I1(cfg_wait_cnt_reg[1]),
        .I2(cfg_wait_cnt_reg[0]),
        .O(\cfg_wait_cnt[5]_i_2_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[0]),
        .Q(cfg_wait_cnt_reg[0]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[1]),
        .Q(cfg_wait_cnt_reg[1]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[2]),
        .Q(cfg_wait_cnt_reg[2]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[3]),
        .Q(cfg_wait_cnt_reg[3]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[4]),
        .Q(cfg_wait_cnt_reg[4]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    \cfg_wait_cnt_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__0[5]),
        .Q(cfg_wait_cnt_reg[5]),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    dclk_rst_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(dclk_rst_reg1_0),
        .Q(dclk_rst_reg1),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    dclk_rst_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(dclk_rst_reg1),
        .Q(SR),
        .R(1'b0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \drp_done_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(done),
        .Q(drp_done_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \drp_done_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(drp_done_reg1),
        .Q(drp_done_reg2),
        .R(reset_n_reg2_reg));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \gtp_common.gtpe2_common_i_i_3 
       (.I0(rst_cpllreset),
        .I1(cpllrst),
        .O(PLL0RESET0));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT3 #(
    .INIT(8'hBA)) 
    gtreset_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[6] ),
        .I2(rst_gtreset),
        .O(gtreset_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    gtreset_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gtreset_i_1_n_0),
        .Q(rst_gtreset),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_mmcm_lock_in),
        .Q(mmcm_lock_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(mmcm_lock_reg1),
        .Q(mmcm_lock_reg2),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \phystatus_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_phystatus),
        .Q(phystatus_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \phystatus_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(phystatus_reg1),
        .Q(phystatus_reg2),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE plllock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(plllock_reg1_reg_0),
        .Q(plllock_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE plllock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(plllock_reg1),
        .Q(plllock_reg2),
        .R(reset_n_reg2_reg));
  (* SOFT_HLUTNM = "soft_lutpair8" *) 
  LUT3 #(
    .INIT(8'hBA)) 
    pllreset_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[12] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[8] ),
        .I2(rst_cpllreset),
        .O(pllreset_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    pllreset_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pllreset_i_1_n_0),
        .Q(rst_cpllreset),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_idle_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(Q[0]),
        .Q(rate_idle_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_idle_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_idle_reg1),
        .Q(rate_idle_reg2),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \resetdone_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(user_resetdone),
        .Q(resetdone_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \resetdone_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(resetdone_reg1),
        .Q(resetdone_reg2),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxcdrlock_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(user_rxcdrlock),
        .Q(rxcdrlock_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxcdrlock_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxcdrlock_reg1),
        .Q(rxcdrlock_reg2),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxpmaresetdone_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rxpmaresetdone_reg1_reg[0]_0 ),
        .Q(rxpmaresetdone_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxpmaresetdone_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxpmaresetdone_reg1),
        .Q(rxpmaresetdone_reg2),
        .R(reset_n_reg2_reg));
  FDRE #(
    .INIT(1'b0)) 
    rxusrclk_rst_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rst_cpllreset),
        .Q(rxusrclk_rst_reg1),
        .R(1'b0));
  (* SOFT_HLUTNM = "soft_lutpair9" *) 
  LUT2 #(
    .INIT(4'hE)) 
    rxusrclk_rst_reg2_i_1
       (.I0(rxusrclk_rst_reg1),
        .I1(rst_cpllreset),
        .O(rxusrclk_rst_reg2_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    rxusrclk_rst_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rxusrclk_rst_reg2_i_1_n_0),
        .Q(rxusrclk_rst_reg2_reg_0),
        .R(1'b0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txsync_done_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_done),
        .Q(txsync_done_reg1),
        .R(reset_n_reg2_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txsync_done_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_done_reg1),
        .Q(txsync_done_reg2),
        .R(reset_n_reg2_reg));
  LUT2 #(
    .INIT(4'hE)) 
    txsync_start_reg1_i_1
       (.I0(rst_txsync_start),
        .I1(Q[1]),
        .O(SYNC_TXSYNC_START0));
  LUT3 #(
    .INIT(8'hB8)) 
    userrdy_i_1
       (.I0(mmcm_lock_reg2),
        .I1(userrdy),
        .I2(rst_userrdy),
        .O(userrdy_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    userrdy_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(userrdy_i_1_n_0),
        .Q(rst_userrdy),
        .R(reset_n_reg2_reg));
endmodule

(* CFG_CTL_IF = "TRUE" *) (* CFG_FC_IF = "TRUE" *) (* CFG_MGMT_IF = "TRUE" *) 
(* CFG_STATUS_IF = "TRUE" *) (* C_DATA_WIDTH = "64" *) (* DowngradeIPIdentifiedWarnings = "yes" *) 
(* ENABLE_JTAG_DBG = "FALSE" *) (* ERR_REPORTING_IF = "TRUE" *) (* EXT_CH_GT_DRP = "FALSE" *) 
(* EXT_PIPE_INTERFACE = "FALSE" *) (* EXT_STARTUP_PRIMITIVE = "FALSE" *) (* KEEP_WIDTH = "8" *) 
(* LINK_CAP_MAX_LINK_WIDTH = "1" *) (* PCIE_ASYNC_EN = "FALSE" *) (* PCIE_EXT_CLK = "TRUE" *) 
(* PCIE_EXT_GT_COMMON = "FALSE" *) (* PCIE_ID_IF = "FALSE" *) (* PIPE_SIM = "FALSE" *) 
(* PL_INTERFACE = "TRUE" *) (* RCV_MSG_IF = "TRUE" *) (* REDUCE_OOB_FREQ = "FALSE" *) 
(* SHARED_LOGIC_IN_CORE = "FALSE" *) (* TRANSCEIVER_CTRL_STATUS_PORTS = "FALSE" *) (* bar_0 = "FFFFFC04" *) 
(* bar_1 = "FFFFFFFF" *) (* bar_2 = "00000000" *) (* bar_3 = "00000000" *) 
(* bar_4 = "00000000" *) (* bar_5 = "00000000" *) (* bram_lat = "0" *) 
(* c_aer_base_ptr = "000" *) (* c_aer_cap_ecrc_check_capable = "FALSE" *) (* c_aer_cap_ecrc_gen_capable = "FALSE" *) 
(* c_aer_cap_multiheader = "FALSE" *) (* c_aer_cap_nextptr = "000" *) (* c_aer_cap_on = "FALSE" *) 
(* c_aer_cap_optional_err_support = "000000" *) (* c_aer_cap_permit_rooterr_update = "FALSE" *) (* c_buf_opt_bma = "TRUE" *) 
(* c_component_name = "pcie_7x_bridge" *) (* c_cpl_inf = "TRUE" *) (* c_cpl_infinite = "TRUE" *) 
(* c_cpl_timeout_disable_sup = "FALSE" *) (* c_cpl_timeout_range = "0010" *) (* c_cpl_timeout_ranges_sup = "2" *) 
(* c_d1_support = "FALSE" *) (* c_d2_support = "FALSE" *) (* c_de_emph = "FALSE" *) 
(* c_dev_cap2_ari_forwarding_supported = "FALSE" *) (* c_dev_cap2_atomicop32_completer_supported = "FALSE" *) (* c_dev_cap2_atomicop64_completer_supported = "FALSE" *) 
(* c_dev_cap2_atomicop_routing_supported = "FALSE" *) (* c_dev_cap2_cas128_completer_supported = "FALSE" *) (* c_dev_cap2_tph_completer_supported = "00" *) 
(* c_dev_control_ext_tag_default = "FALSE" *) (* c_dev_port_type = "0" *) (* c_dis_lane_reverse = "TRUE" *) 
(* c_disable_rx_poisoned_resp = "FALSE" *) (* c_disable_scrambling = "FALSE" *) (* c_disable_tx_aspm_l0s = "FALSE" *) 
(* c_dll_lnk_actv_cap = "FALSE" *) (* c_dsi_bool = "FALSE" *) (* c_dsn_base_ptr = "100" *) 
(* c_dsn_cap_enabled = "TRUE" *) (* c_dsn_next_ptr = "000" *) (* c_enable_msg_route = "00000000000" *) 
(* c_ep_l0s_accpt_lat = "0" *) (* c_ep_l1_accpt_lat = "7" *) (* c_ext_pci_cfg_space_addr = "3FF" *) 
(* c_external_clocking = "TRUE" *) (* c_fc_cpld = "461" *) (* c_fc_cplh = "36" *) 
(* c_fc_npd = "24" *) (* c_fc_nph = "12" *) (* c_fc_pd = "437" *) 
(* c_fc_ph = "32" *) (* c_gen1 = "1'b0" *) (* c_header_type = "00" *) 
(* c_hw_auton_spd_disable = "FALSE" *) (* c_int_width = "64" *) (* c_last_cfg_dw = "10C" *) 
(* c_link_cap_aspm_optionality = "FALSE" *) (* c_ll_ack_timeout = "0000" *) (* c_ll_ack_timeout_enable = "FALSE" *) 
(* c_ll_ack_timeout_function = "0" *) (* c_ll_replay_timeout = "0000" *) (* c_ll_replay_timeout_enable = "FALSE" *) 
(* c_ll_replay_timeout_func = "1" *) (* c_lnk_bndwdt_notif = "FALSE" *) (* c_msi = "0" *) 
(* c_msi_64b_addr = "TRUE" *) (* c_msi_cap_on = "TRUE" *) (* c_msi_mult_msg_extn = "0" *) 
(* c_msi_per_vctr_mask_cap = "FALSE" *) (* c_msix_cap_on = "TRUE" *) (* c_msix_next_ptr = "00" *) 
(* c_msix_pba_bir = "0" *) (* c_msix_pba_offset = "0" *) (* c_msix_table_bir = "0" *) 
(* c_msix_table_offset = "0" *) (* c_msix_table_size = "000" *) (* c_pci_cfg_space_addr = "3F" *) 
(* c_pcie_blk_locn = "0" *) (* c_pcie_cap_next_ptr = "9C" *) (* c_pcie_cap_slot_implemented = "FALSE" *) 
(* c_pcie_dbg_ports = "TRUE" *) (* c_pcie_fast_config = "0" *) (* c_perf_level_high = "TRUE" *) 
(* c_phantom_functions = "0" *) (* c_pm_cap_next_ptr = "48" *) (* c_pme_support = "0F" *) 
(* c_rbar_base_ptr = "000" *) (* c_rbar_cap_control_encodedbar0 = "00" *) (* c_rbar_cap_control_encodedbar1 = "00" *) 
(* c_rbar_cap_control_encodedbar2 = "00" *) (* c_rbar_cap_control_encodedbar3 = "00" *) (* c_rbar_cap_control_encodedbar4 = "00" *) 
(* c_rbar_cap_control_encodedbar5 = "00" *) (* c_rbar_cap_index0 = "0" *) (* c_rbar_cap_index1 = "0" *) 
(* c_rbar_cap_index2 = "0" *) (* c_rbar_cap_index3 = "0" *) (* c_rbar_cap_index4 = "0" *) 
(* c_rbar_cap_index5 = "0" *) (* c_rbar_cap_nextptr = "000" *) (* c_rbar_cap_on = "FALSE" *) 
(* c_rbar_cap_sup0 = "00001" *) (* c_rbar_cap_sup1 = "00001" *) (* c_rbar_cap_sup2 = "00001" *) 
(* c_rbar_cap_sup3 = "00001" *) (* c_rbar_cap_sup4 = "00001" *) (* c_rbar_cap_sup5 = "00001" *) 
(* c_rbar_num = "0" *) (* c_rcb = "0" *) (* c_recrc_check = "0" *) 
(* c_recrc_check_trim = "FALSE" *) (* c_rev_gt_order = "FALSE" *) (* c_root_cap_crs = "FALSE" *) 
(* c_rx_raddr_lat = "0" *) (* c_rx_ram_limit = "7FF" *) (* c_rx_rdata_lat = "2" *) 
(* c_rx_write_lat = "0" *) (* c_silicon_rev = "2" *) (* c_slot_cap_attn_butn = "FALSE" *) 
(* c_slot_cap_attn_ind = "FALSE" *) (* c_slot_cap_elec_interlock = "FALSE" *) (* c_slot_cap_hotplug_cap = "FALSE" *) 
(* c_slot_cap_hotplug_surprise = "FALSE" *) (* c_slot_cap_mrl = "FALSE" *) (* c_slot_cap_no_cmd_comp_sup = "FALSE" *) 
(* c_slot_cap_physical_slot_num = "0" *) (* c_slot_cap_pwr_ctrl = "FALSE" *) (* c_slot_cap_pwr_ind = "FALSE" *) 
(* c_slot_cap_pwr_limit_scale = "0" *) (* c_slot_cap_pwr_limit_value = "0" *) (* c_surprise_dn_err_cap = "FALSE" *) 
(* c_trgt_lnk_spd = "0" *) (* c_trn_np_fc = "TRUE" *) (* c_tx_last_tlp = "29" *) 
(* c_tx_raddr_lat = "0" *) (* c_tx_rdata_lat = "2" *) (* c_tx_write_lat = "0" *) 
(* c_upconfig_capable = "TRUE" *) (* c_upstream_facing = "TRUE" *) (* c_ur_atomic = "FALSE" *) 
(* c_ur_inv_req = "TRUE" *) (* c_ur_prs_response = "TRUE" *) (* c_vc_base_ptr = "000" *) 
(* c_vc_cap_enabled = "FALSE" *) (* c_vc_cap_reject_snoop = "FALSE" *) (* c_vc_next_ptr = "000" *) 
(* c_vsec_base_ptr = "000" *) (* c_vsec_cap_enabled = "FALSE" *) (* c_vsec_next_ptr = "000" *) 
(* c_xlnx_ref_board = "NONE" *) (* cap_ver = "2" *) (* cardbus_cis_ptr = "00000000" *) 
(* class_code = "020000" *) (* cmps = "2" *) (* con_scl_fctr_d0_state = "0" *) 
(* con_scl_fctr_d1_state = "0" *) (* con_scl_fctr_d2_state = "0" *) (* con_scl_fctr_d3_state = "0" *) 
(* cost_table = "1" *) (* d1_sup = "0" *) (* d2_sup = "0" *) 
(* dev_id = "8125" *) (* dev_port_type = "0000" *) (* dis_scl_fctr_d0_state = "0" *) 
(* dis_scl_fctr_d1_state = "0" *) (* dis_scl_fctr_d2_state = "0" *) (* dis_scl_fctr_d3_state = "0" *) 
(* dsi = "0" *) (* ep_l0s_accpt_lat = "000" *) (* ep_l1_accpt_lat = "111" *) 
(* ext_tag_fld_sup = "FALSE" *) (* int_pin = "1" *) (* intx = "TRUE" *) 
(* max_lnk_spd = "1" *) (* max_lnk_wdt = "000001" *) (* mps = "010" *) 
(* no_soft_rst = "TRUE" *) (* pci_exp_int_freq = "1" *) (* pci_exp_ref_freq = "0" *) 
(* phantm_func_sup = "00" *) (* pme_sup = "0F" *) (* pwr_con_d0_state = "00" *) 
(* pwr_con_d1_state = "00" *) (* pwr_con_d2_state = "00" *) (* pwr_con_d3_state = "00" *) 
(* pwr_dis_d0_state = "00" *) (* pwr_dis_d1_state = "00" *) (* pwr_dis_d2_state = "00" *) 
(* pwr_dis_d3_state = "00" *) (* rev_id = "04" *) (* slot_clk = "TRUE" *) 
(* subsys_id = "7" *) (* subsys_ven_id = "4332" *) (* ven_id = "10ec" *) 
(* xrom_bar = "00000000" *) 
module pcie_7x_bridge_pcie2_top
   (pci_exp_txn,
    pci_exp_txp,
    pci_exp_rxn,
    pci_exp_rxp,
    int_pclk_out_slave,
    int_pipe_rxusrclk_out,
    int_rxoutclk_out,
    int_dclk_out,
    int_userclk1_out,
    int_userclk2_out,
    int_oobclk_out,
    int_mmcm_lock_out,
    int_qplllock_out,
    int_qplloutclk_out,
    int_qplloutrefclk_out,
    int_pclk_sel_slave,
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
    qpll_drp_crscode,
    qpll_drp_fsm,
    qpll_drp_done,
    qpll_drp_reset,
    qpll_qplllock,
    qpll_qplloutclk,
    qpll_qplloutrefclk,
    qpll_qplld,
    qpll_qpllreset,
    qpll_drp_clk,
    qpll_drp_rst_n,
    qpll_drp_ovrd,
    qpll_drp_gen3,
    qpll_drp_start,
    user_clk_out,
    user_reset_out,
    user_lnk_up,
    user_app_rdy,
    tx_buf_av,
    tx_err_drop,
    tx_cfg_req,
    s_axis_tx_tdata,
    s_axis_tx_tvalid,
    s_axis_tx_tready,
    s_axis_tx_tkeep,
    s_axis_tx_tlast,
    s_axis_tx_tuser,
    tx_cfg_gnt,
    m_axis_rx_tdata,
    m_axis_rx_tvalid,
    m_axis_rx_tready,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
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
    cfg_msg_received,
    cfg_msg_data,
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
    cfg_msg_received_pm_as_nak,
    cfg_msg_received_setslotpowerlimit,
    cfg_pm_send_pme_to,
    cfg_ds_bus_number,
    cfg_ds_device_number,
    cfg_ds_function_number,
    cfg_mgmt_wr_rw1c_as_rw,
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
    pcie_drp_clk,
    pcie_drp_en,
    pcie_drp_we,
    pcie_drp_addr,
    pcie_drp_di,
    pcie_drp_rdy,
    pcie_drp_do,
    startup_eos_in,
    startup_cfgclk,
    startup_cfgmclk,
    startup_eos,
    startup_preq,
    startup_clk,
    startup_gsr,
    startup_gts,
    startup_keyclearb,
    startup_pack,
    startup_usrcclko,
    startup_usrcclkts,
    startup_usrdoneo,
    startup_usrdonets,
    icap_clk,
    icap_csib,
    icap_rdwrb,
    icap_i,
    icap_o,
    pipe_txprbssel,
    pipe_rxprbssel,
    pipe_txprbsforceerr,
    pipe_rxprbscntreset,
    pipe_loopback,
    pipe_rxprbserr,
    pipe_txinhibit,
    pipe_rst_fsm,
    pipe_qrst_fsm,
    pipe_rate_fsm,
    pipe_sync_fsm_tx,
    pipe_sync_fsm_rx,
    pipe_drp_fsm,
    pipe_rst_idle,
    pipe_qrst_idle,
    pipe_rate_idle,
    pipe_eyescandataerror,
    pipe_rxstatus,
    pipe_dmonitorout,
    pipe_cpll_lock,
    pipe_qpll_lock,
    pipe_rxpmaresetdone,
    pipe_rxbufstatus,
    pipe_txphaligndone,
    pipe_txphinitdone,
    pipe_txdlysresetdone,
    pipe_rxphaligndone,
    pipe_rxdlysresetdone,
    pipe_rxsyncdone,
    pipe_rxdisperr,
    pipe_rxnotintable,
    pipe_rxcommadet,
    gt_ch_drp_rdy,
    pipe_debug_0,
    pipe_debug_1,
    pipe_debug_2,
    pipe_debug_3,
    pipe_debug_4,
    pipe_debug_5,
    pipe_debug_6,
    pipe_debug_7,
    pipe_debug_8,
    pipe_debug_9,
    pipe_debug,
    ext_ch_gt_drpclk,
    ext_ch_gt_drpaddr,
    ext_ch_gt_drpen,
    ext_ch_gt_drpdi,
    ext_ch_gt_drpwe,
    ext_ch_gt_drpdo,
    ext_ch_gt_drprdy,
    common_commands_in,
    pipe_rx_0_sigs,
    pipe_rx_1_sigs,
    pipe_rx_2_sigs,
    pipe_rx_3_sigs,
    pipe_rx_4_sigs,
    pipe_rx_5_sigs,
    pipe_rx_6_sigs,
    pipe_rx_7_sigs,
    common_commands_out,
    pipe_tx_0_sigs,
    pipe_tx_1_sigs,
    pipe_tx_2_sigs,
    pipe_tx_3_sigs,
    pipe_tx_4_sigs,
    pipe_tx_5_sigs,
    pipe_tx_6_sigs,
    pipe_tx_7_sigs,
    cfg_dev_id_pf0,
    cfg_ven_id,
    cfg_rev_id_pf0,
    cfg_subsys_id_pf0,
    cfg_subsys_ven_id,
    pipe_mmcm_rst_n,
    sys_clk,
    sys_rst_n);
  output [0:0]pci_exp_txn;
  output [0:0]pci_exp_txp;
  input [0:0]pci_exp_rxn;
  input [0:0]pci_exp_rxp;
  output int_pclk_out_slave;
  output int_pipe_rxusrclk_out;
  output [0:0]int_rxoutclk_out;
  output int_dclk_out;
  output int_userclk1_out;
  output int_userclk2_out;
  output int_oobclk_out;
  output int_mmcm_lock_out;
  output [1:0]int_qplllock_out;
  output [1:0]int_qplloutclk_out;
  output [1:0]int_qplloutrefclk_out;
  input [0:0]int_pclk_sel_slave;
  input pipe_pclk_in;
  input pipe_rxusrclk_in;
  input [0:0]pipe_rxoutclk_in;
  input pipe_dclk_in;
  input pipe_userclk1_in;
  input pipe_userclk2_in;
  input pipe_oobclk_in;
  input pipe_mmcm_lock_in;
  output pipe_txoutclk_out;
  output [0:0]pipe_rxoutclk_out;
  output [0:0]pipe_pclk_sel_out;
  output pipe_gen3_out;
  input [11:0]qpll_drp_crscode;
  input [17:0]qpll_drp_fsm;
  input [1:0]qpll_drp_done;
  input [1:0]qpll_drp_reset;
  input [1:0]qpll_qplllock;
  input [1:0]qpll_qplloutclk;
  input [1:0]qpll_qplloutrefclk;
  output qpll_qplld;
  output [1:0]qpll_qpllreset;
  output qpll_drp_clk;
  output qpll_drp_rst_n;
  output qpll_drp_ovrd;
  output qpll_drp_gen3;
  output qpll_drp_start;
  output user_clk_out;
  output user_reset_out;
  output user_lnk_up;
  output user_app_rdy;
  output [5:0]tx_buf_av;
  output tx_err_drop;
  output tx_cfg_req;
  input [63:0]s_axis_tx_tdata;
  input s_axis_tx_tvalid;
  output s_axis_tx_tready;
  input [7:0]s_axis_tx_tkeep;
  input s_axis_tx_tlast;
  input [3:0]s_axis_tx_tuser;
  input tx_cfg_gnt;
  output [63:0]m_axis_rx_tdata;
  output m_axis_rx_tvalid;
  input m_axis_rx_tready;
  output [7:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output [21:0]m_axis_rx_tuser;
  input rx_np_ok;
  input rx_np_req;
  output [11:0]fc_cpld;
  output [7:0]fc_cplh;
  output [11:0]fc_npd;
  output [7:0]fc_nph;
  output [11:0]fc_pd;
  output [7:0]fc_ph;
  input [2:0]fc_sel;
  output [31:0]cfg_mgmt_do;
  output cfg_mgmt_rd_wr_done;
  output [15:0]cfg_status;
  output [15:0]cfg_command;
  output [15:0]cfg_dstatus;
  output [15:0]cfg_dcommand;
  output [15:0]cfg_lstatus;
  output [15:0]cfg_lcommand;
  output [15:0]cfg_dcommand2;
  output [2:0]cfg_pcie_link_state;
  output cfg_pmcsr_pme_en;
  output [1:0]cfg_pmcsr_powerstate;
  output cfg_pmcsr_pme_status;
  output cfg_received_func_lvl_rst;
  input [31:0]cfg_mgmt_di;
  input [3:0]cfg_mgmt_byte_en;
  input [9:0]cfg_mgmt_dwaddr;
  input cfg_mgmt_wr_en;
  input cfg_mgmt_rd_en;
  input cfg_mgmt_wr_readonly;
  input cfg_err_ecrc;
  input cfg_err_ur;
  input cfg_err_cpl_timeout;
  input cfg_err_cpl_unexpect;
  input cfg_err_cpl_abort;
  input cfg_err_posted;
  input cfg_err_cor;
  input cfg_err_atomic_egress_blocked;
  input cfg_err_internal_cor;
  input cfg_err_malformed;
  input cfg_err_mc_blocked;
  input cfg_err_poisoned;
  input cfg_err_norecovery;
  input [47:0]cfg_err_tlp_cpl_header;
  output cfg_err_cpl_rdy;
  input cfg_err_locked;
  input cfg_err_acs;
  input cfg_err_internal_uncor;
  input cfg_trn_pending;
  input cfg_pm_halt_aspm_l0s;
  input cfg_pm_halt_aspm_l1;
  input cfg_pm_force_state_en;
  input [1:0]cfg_pm_force_state;
  input [63:0]cfg_dsn;
  output cfg_msg_received;
  output [15:0]cfg_msg_data;
  input cfg_interrupt;
  output cfg_interrupt_rdy;
  input cfg_interrupt_assert;
  input [7:0]cfg_interrupt_di;
  output [7:0]cfg_interrupt_do;
  output [2:0]cfg_interrupt_mmenable;
  output cfg_interrupt_msienable;
  output cfg_interrupt_msixenable;
  output cfg_interrupt_msixfm;
  input cfg_interrupt_stat;
  input [4:0]cfg_pciecap_interrupt_msgnum;
  output cfg_to_turnoff;
  input cfg_turnoff_ok;
  output [7:0]cfg_bus_number;
  output [4:0]cfg_device_number;
  output [2:0]cfg_function_number;
  input cfg_pm_wake;
  output cfg_msg_received_pm_as_nak;
  output cfg_msg_received_setslotpowerlimit;
  input cfg_pm_send_pme_to;
  input [7:0]cfg_ds_bus_number;
  input [4:0]cfg_ds_device_number;
  input [2:0]cfg_ds_function_number;
  input cfg_mgmt_wr_rw1c_as_rw;
  output cfg_bridge_serr_en;
  output cfg_slot_control_electromech_il_ctl_pulse;
  output cfg_root_control_syserr_corr_err_en;
  output cfg_root_control_syserr_non_fatal_err_en;
  output cfg_root_control_syserr_fatal_err_en;
  output cfg_root_control_pme_int_en;
  output cfg_aer_rooterr_corr_err_reporting_en;
  output cfg_aer_rooterr_non_fatal_err_reporting_en;
  output cfg_aer_rooterr_fatal_err_reporting_en;
  output cfg_aer_rooterr_corr_err_received;
  output cfg_aer_rooterr_non_fatal_err_received;
  output cfg_aer_rooterr_fatal_err_received;
  output cfg_msg_received_err_cor;
  output cfg_msg_received_err_non_fatal;
  output cfg_msg_received_err_fatal;
  output cfg_msg_received_pm_pme;
  output cfg_msg_received_pme_to_ack;
  output cfg_msg_received_assert_int_a;
  output cfg_msg_received_assert_int_b;
  output cfg_msg_received_assert_int_c;
  output cfg_msg_received_assert_int_d;
  output cfg_msg_received_deassert_int_a;
  output cfg_msg_received_deassert_int_b;
  output cfg_msg_received_deassert_int_c;
  output cfg_msg_received_deassert_int_d;
  input [1:0]pl_directed_link_change;
  input [1:0]pl_directed_link_width;
  input pl_directed_link_speed;
  input pl_directed_link_auton;
  input pl_upstream_prefer_deemph;
  output pl_sel_lnk_rate;
  output [1:0]pl_sel_lnk_width;
  output [5:0]pl_ltssm_state;
  output [1:0]pl_lane_reversal_mode;
  output pl_phy_lnk_up;
  output [2:0]pl_tx_pm_state;
  output [1:0]pl_rx_pm_state;
  output pl_link_upcfg_cap;
  output pl_link_gen2_cap;
  output pl_link_partner_gen2_supported;
  output [2:0]pl_initial_link_width;
  output pl_directed_change_done;
  output pl_received_hot_rst;
  input pl_transmit_hot_rst;
  input pl_downstream_deemph_source;
  input [127:0]cfg_err_aer_headerlog;
  input [4:0]cfg_aer_interrupt_msgnum;
  output cfg_err_aer_headerlog_set;
  output cfg_aer_ecrc_check_en;
  output cfg_aer_ecrc_gen_en;
  output [6:0]cfg_vc_tcvc_map;
  input pcie_drp_clk;
  input pcie_drp_en;
  input pcie_drp_we;
  input [8:0]pcie_drp_addr;
  input [15:0]pcie_drp_di;
  output pcie_drp_rdy;
  output [15:0]pcie_drp_do;
  input startup_eos_in;
  output startup_cfgclk;
  output startup_cfgmclk;
  output startup_eos;
  output startup_preq;
  input startup_clk;
  input startup_gsr;
  input startup_gts;
  input startup_keyclearb;
  input startup_pack;
  input startup_usrcclko;
  input startup_usrcclkts;
  input startup_usrdoneo;
  input startup_usrdonets;
  input icap_clk;
  input icap_csib;
  input icap_rdwrb;
  input [31:0]icap_i;
  output [31:0]icap_o;
  input [2:0]pipe_txprbssel;
  input [2:0]pipe_rxprbssel;
  input pipe_txprbsforceerr;
  input pipe_rxprbscntreset;
  input [2:0]pipe_loopback;
  output [0:0]pipe_rxprbserr;
  input [0:0]pipe_txinhibit;
  output [4:0]pipe_rst_fsm;
  output [11:0]pipe_qrst_fsm;
  output [4:0]pipe_rate_fsm;
  output [5:0]pipe_sync_fsm_tx;
  output [6:0]pipe_sync_fsm_rx;
  output [6:0]pipe_drp_fsm;
  output pipe_rst_idle;
  output pipe_qrst_idle;
  output pipe_rate_idle;
  output [0:0]pipe_eyescandataerror;
  output [2:0]pipe_rxstatus;
  output [14:0]pipe_dmonitorout;
  output [0:0]pipe_cpll_lock;
  output [0:0]pipe_qpll_lock;
  output [0:0]pipe_rxpmaresetdone;
  output [2:0]pipe_rxbufstatus;
  output [0:0]pipe_txphaligndone;
  output [0:0]pipe_txphinitdone;
  output [0:0]pipe_txdlysresetdone;
  output [0:0]pipe_rxphaligndone;
  output [0:0]pipe_rxdlysresetdone;
  output [0:0]pipe_rxsyncdone;
  output [7:0]pipe_rxdisperr;
  output [7:0]pipe_rxnotintable;
  output [0:0]pipe_rxcommadet;
  output [0:0]gt_ch_drp_rdy;
  output [0:0]pipe_debug_0;
  output [0:0]pipe_debug_1;
  output [0:0]pipe_debug_2;
  output [0:0]pipe_debug_3;
  output [0:0]pipe_debug_4;
  output [0:0]pipe_debug_5;
  output [0:0]pipe_debug_6;
  output [0:0]pipe_debug_7;
  output [0:0]pipe_debug_8;
  output [0:0]pipe_debug_9;
  output [31:0]pipe_debug;
  output ext_ch_gt_drpclk;
  input [8:0]ext_ch_gt_drpaddr;
  input [0:0]ext_ch_gt_drpen;
  input [15:0]ext_ch_gt_drpdi;
  input [0:0]ext_ch_gt_drpwe;
  output [15:0]ext_ch_gt_drpdo;
  output [0:0]ext_ch_gt_drprdy;
  input [11:0]common_commands_in;
  input [24:0]pipe_rx_0_sigs;
  input [24:0]pipe_rx_1_sigs;
  input [24:0]pipe_rx_2_sigs;
  input [24:0]pipe_rx_3_sigs;
  input [24:0]pipe_rx_4_sigs;
  input [24:0]pipe_rx_5_sigs;
  input [24:0]pipe_rx_6_sigs;
  input [24:0]pipe_rx_7_sigs;
  output [11:0]common_commands_out;
  output [24:0]pipe_tx_0_sigs;
  output [24:0]pipe_tx_1_sigs;
  output [24:0]pipe_tx_2_sigs;
  output [24:0]pipe_tx_3_sigs;
  output [24:0]pipe_tx_4_sigs;
  output [24:0]pipe_tx_5_sigs;
  output [24:0]pipe_tx_6_sigs;
  output [24:0]pipe_tx_7_sigs;
  input [15:0]cfg_dev_id_pf0;
  input [15:0]cfg_ven_id;
  input [7:0]cfg_rev_id_pf0;
  input [15:0]cfg_subsys_id_pf0;
  input [15:0]cfg_subsys_ven_id;
  input pipe_mmcm_rst_n;
  input sys_clk;
  input sys_rst_n;

  wire \<const0> ;
  wire cfg_aer_ecrc_check_en;
  wire cfg_aer_ecrc_gen_en;
  wire [4:0]cfg_aer_interrupt_msgnum;
  wire cfg_aer_rooterr_corr_err_received;
  wire cfg_aer_rooterr_corr_err_reporting_en;
  wire cfg_aer_rooterr_fatal_err_received;
  wire cfg_aer_rooterr_fatal_err_reporting_en;
  wire cfg_aer_rooterr_non_fatal_err_received;
  wire cfg_aer_rooterr_non_fatal_err_reporting_en;
  wire cfg_bridge_serr_en;
  wire [7:0]cfg_bus_number;
  wire [10:0]\^cfg_command ;
  wire [14:0]\^cfg_dcommand ;
  wire [11:0]\^cfg_dcommand2 ;
  wire [4:0]cfg_device_number;
  wire [7:0]cfg_ds_bus_number;
  wire [4:0]cfg_ds_device_number;
  wire [2:0]cfg_ds_function_number;
  wire [63:0]cfg_dsn;
  wire [3:0]\^cfg_dstatus ;
  wire [127:0]cfg_err_aer_headerlog;
  wire cfg_err_aer_headerlog_set;
  wire cfg_err_atomic_egress_blocked;
  wire cfg_err_cor;
  wire cfg_err_cpl_abort;
  wire cfg_err_cpl_rdy;
  wire cfg_err_cpl_timeout;
  wire cfg_err_cpl_unexpect;
  wire cfg_err_ecrc;
  wire cfg_err_internal_cor;
  wire cfg_err_internal_uncor;
  wire cfg_err_locked;
  wire cfg_err_malformed;
  wire cfg_err_mc_blocked;
  wire cfg_err_norecovery;
  wire cfg_err_poisoned;
  wire cfg_err_posted;
  wire [47:0]cfg_err_tlp_cpl_header;
  wire cfg_err_ur;
  wire [2:0]cfg_function_number;
  wire cfg_interrupt;
  wire cfg_interrupt_assert;
  wire [7:0]cfg_interrupt_di;
  wire [7:0]cfg_interrupt_do;
  wire [2:0]cfg_interrupt_mmenable;
  wire cfg_interrupt_msienable;
  wire cfg_interrupt_msixenable;
  wire cfg_interrupt_msixfm;
  wire cfg_interrupt_rdy;
  wire cfg_interrupt_stat;
  wire [11:0]\^cfg_lcommand ;
  wire [15:0]\^cfg_lstatus ;
  wire [3:0]cfg_mgmt_byte_en;
  wire [31:0]cfg_mgmt_di;
  wire [31:0]cfg_mgmt_do;
  wire [9:0]cfg_mgmt_dwaddr;
  wire cfg_mgmt_rd_en;
  wire cfg_mgmt_rd_wr_done;
  wire cfg_mgmt_wr_en;
  wire cfg_mgmt_wr_readonly;
  wire cfg_mgmt_wr_rw1c_as_rw;
  wire [15:0]cfg_msg_data;
  wire cfg_msg_received;
  wire cfg_msg_received_assert_int_a;
  wire cfg_msg_received_assert_int_b;
  wire cfg_msg_received_assert_int_c;
  wire cfg_msg_received_assert_int_d;
  wire cfg_msg_received_deassert_int_a;
  wire cfg_msg_received_deassert_int_b;
  wire cfg_msg_received_deassert_int_c;
  wire cfg_msg_received_deassert_int_d;
  wire cfg_msg_received_err_cor;
  wire cfg_msg_received_err_fatal;
  wire cfg_msg_received_err_non_fatal;
  wire cfg_msg_received_pm_as_nak;
  wire cfg_msg_received_pm_pme;
  wire cfg_msg_received_pme_to_ack;
  wire cfg_msg_received_setslotpowerlimit;
  wire [2:0]cfg_pcie_link_state;
  wire [4:0]cfg_pciecap_interrupt_msgnum;
  wire [1:0]cfg_pm_force_state;
  wire cfg_pm_force_state_en;
  wire cfg_pm_halt_aspm_l0s;
  wire cfg_pm_halt_aspm_l1;
  wire cfg_pm_wake;
  wire cfg_pmcsr_pme_en;
  wire cfg_pmcsr_pme_status;
  wire [1:0]cfg_pmcsr_powerstate;
  wire cfg_received_func_lvl_rst;
  wire cfg_root_control_pme_int_en;
  wire cfg_root_control_syserr_corr_err_en;
  wire cfg_root_control_syserr_fatal_err_en;
  wire cfg_root_control_syserr_non_fatal_err_en;
  wire cfg_slot_control_electromech_il_ctl_pulse;
  wire cfg_to_turnoff;
  wire cfg_trn_pending;
  wire cfg_turnoff_ok;
  wire [6:0]cfg_vc_tcvc_map;
  wire [11:0]fc_cpld;
  wire [7:0]fc_cplh;
  wire [11:0]fc_npd;
  wire [7:0]fc_nph;
  wire [11:0]fc_pd;
  wire [7:0]fc_ph;
  wire [2:0]fc_sel;
  wire [63:0]m_axis_rx_tdata;
  wire [6:6]\^m_axis_rx_tkeep ;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [21:0]\^m_axis_rx_tuser ;
  wire m_axis_rx_tvalid;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire [8:0]pcie_drp_addr;
  wire pcie_drp_clk;
  wire [15:0]pcie_drp_di;
  wire [15:0]pcie_drp_do;
  wire pcie_drp_en;
  wire pcie_drp_rdy;
  wire pcie_drp_we;
  wire pipe_dclk_in;
  wire pipe_mmcm_lock_in;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire pipe_txoutclk_out;
  wire pipe_userclk1_in;
  wire pipe_userclk2_in;
  wire pl_directed_change_done;
  wire pl_directed_link_auton;
  wire [1:0]pl_directed_link_change;
  wire pl_directed_link_speed;
  wire [1:0]pl_directed_link_width;
  wire pl_downstream_deemph_source;
  wire [2:0]pl_initial_link_width;
  wire [1:0]pl_lane_reversal_mode;
  wire pl_link_gen2_cap;
  wire pl_link_partner_gen2_supported;
  wire pl_link_upcfg_cap;
  wire [5:0]pl_ltssm_state;
  wire pl_phy_lnk_up;
  wire pl_received_hot_rst;
  wire [1:0]pl_rx_pm_state;
  wire pl_sel_lnk_rate;
  wire [1:0]pl_sel_lnk_width;
  wire pl_transmit_hot_rst;
  wire [2:0]pl_tx_pm_state;
  wire pl_upstream_prefer_deemph;
  wire rx_np_ok;
  wire rx_np_req;
  wire [63:0]s_axis_tx_tdata;
  wire [7:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire s_axis_tx_tready;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire sys_clk;
  wire sys_rst_n;
  wire [5:0]tx_buf_av;
  wire tx_cfg_gnt;
  wire tx_cfg_req;
  wire tx_err_drop;
  wire user_lnk_up;
  wire user_reset_out;

  assign cfg_command[15] = \<const0> ;
  assign cfg_command[14] = \<const0> ;
  assign cfg_command[13] = \<const0> ;
  assign cfg_command[12] = \<const0> ;
  assign cfg_command[11] = \<const0> ;
  assign cfg_command[10] = \^cfg_command [10];
  assign cfg_command[9] = \<const0> ;
  assign cfg_command[8] = \^cfg_command [8];
  assign cfg_command[7] = \<const0> ;
  assign cfg_command[6] = \<const0> ;
  assign cfg_command[5] = \<const0> ;
  assign cfg_command[4] = \<const0> ;
  assign cfg_command[3] = \<const0> ;
  assign cfg_command[2:0] = \^cfg_command [2:0];
  assign cfg_dcommand[15] = \<const0> ;
  assign cfg_dcommand[14:0] = \^cfg_dcommand [14:0];
  assign cfg_dcommand2[15] = \<const0> ;
  assign cfg_dcommand2[14] = \<const0> ;
  assign cfg_dcommand2[13] = \<const0> ;
  assign cfg_dcommand2[12] = \<const0> ;
  assign cfg_dcommand2[11:0] = \^cfg_dcommand2 [11:0];
  assign cfg_dstatus[15] = \<const0> ;
  assign cfg_dstatus[14] = \<const0> ;
  assign cfg_dstatus[13] = \<const0> ;
  assign cfg_dstatus[12] = \<const0> ;
  assign cfg_dstatus[11] = \<const0> ;
  assign cfg_dstatus[10] = \<const0> ;
  assign cfg_dstatus[9] = \<const0> ;
  assign cfg_dstatus[8] = \<const0> ;
  assign cfg_dstatus[7] = \<const0> ;
  assign cfg_dstatus[6] = \<const0> ;
  assign cfg_dstatus[5] = cfg_trn_pending;
  assign cfg_dstatus[4] = \<const0> ;
  assign cfg_dstatus[3:0] = \^cfg_dstatus [3:0];
  assign cfg_lcommand[15] = \<const0> ;
  assign cfg_lcommand[14] = \<const0> ;
  assign cfg_lcommand[13] = \<const0> ;
  assign cfg_lcommand[12] = \<const0> ;
  assign cfg_lcommand[11:3] = \^cfg_lcommand [11:3];
  assign cfg_lcommand[2] = \<const0> ;
  assign cfg_lcommand[1:0] = \^cfg_lcommand [1:0];
  assign cfg_lstatus[15:13] = \^cfg_lstatus [15:13];
  assign cfg_lstatus[12] = \<const0> ;
  assign cfg_lstatus[11] = \^cfg_lstatus [11];
  assign cfg_lstatus[10] = \<const0> ;
  assign cfg_lstatus[9] = \<const0> ;
  assign cfg_lstatus[8] = \<const0> ;
  assign cfg_lstatus[7:4] = \^cfg_lstatus [7:4];
  assign cfg_lstatus[3] = \<const0> ;
  assign cfg_lstatus[2] = \<const0> ;
  assign cfg_lstatus[1:0] = \^cfg_lstatus [1:0];
  assign cfg_status[15] = \<const0> ;
  assign cfg_status[14] = \<const0> ;
  assign cfg_status[13] = \<const0> ;
  assign cfg_status[12] = \<const0> ;
  assign cfg_status[11] = \<const0> ;
  assign cfg_status[10] = \<const0> ;
  assign cfg_status[9] = \<const0> ;
  assign cfg_status[8] = \<const0> ;
  assign cfg_status[7] = \<const0> ;
  assign cfg_status[6] = \<const0> ;
  assign cfg_status[5] = \<const0> ;
  assign cfg_status[4] = \<const0> ;
  assign cfg_status[3] = \<const0> ;
  assign cfg_status[2] = \<const0> ;
  assign cfg_status[1] = \<const0> ;
  assign cfg_status[0] = \<const0> ;
  assign common_commands_out[11] = \<const0> ;
  assign common_commands_out[10] = \<const0> ;
  assign common_commands_out[9] = \<const0> ;
  assign common_commands_out[8] = \<const0> ;
  assign common_commands_out[7] = \<const0> ;
  assign common_commands_out[6] = \<const0> ;
  assign common_commands_out[5] = \<const0> ;
  assign common_commands_out[4] = \<const0> ;
  assign common_commands_out[3] = \<const0> ;
  assign common_commands_out[2] = \<const0> ;
  assign common_commands_out[1] = \<const0> ;
  assign common_commands_out[0] = \<const0> ;
  assign ext_ch_gt_drpclk = \<const0> ;
  assign ext_ch_gt_drpdo[15] = \<const0> ;
  assign ext_ch_gt_drpdo[14] = \<const0> ;
  assign ext_ch_gt_drpdo[13] = \<const0> ;
  assign ext_ch_gt_drpdo[12] = \<const0> ;
  assign ext_ch_gt_drpdo[11] = \<const0> ;
  assign ext_ch_gt_drpdo[10] = \<const0> ;
  assign ext_ch_gt_drpdo[9] = \<const0> ;
  assign ext_ch_gt_drpdo[8] = \<const0> ;
  assign ext_ch_gt_drpdo[7] = \<const0> ;
  assign ext_ch_gt_drpdo[6] = \<const0> ;
  assign ext_ch_gt_drpdo[5] = \<const0> ;
  assign ext_ch_gt_drpdo[4] = \<const0> ;
  assign ext_ch_gt_drpdo[3] = \<const0> ;
  assign ext_ch_gt_drpdo[2] = \<const0> ;
  assign ext_ch_gt_drpdo[1] = \<const0> ;
  assign ext_ch_gt_drpdo[0] = \<const0> ;
  assign ext_ch_gt_drprdy[0] = \<const0> ;
  assign gt_ch_drp_rdy[0] = \<const0> ;
  assign icap_o[31] = \<const0> ;
  assign icap_o[30] = \<const0> ;
  assign icap_o[29] = \<const0> ;
  assign icap_o[28] = \<const0> ;
  assign icap_o[27] = \<const0> ;
  assign icap_o[26] = \<const0> ;
  assign icap_o[25] = \<const0> ;
  assign icap_o[24] = \<const0> ;
  assign icap_o[23] = \<const0> ;
  assign icap_o[22] = \<const0> ;
  assign icap_o[21] = \<const0> ;
  assign icap_o[20] = \<const0> ;
  assign icap_o[19] = \<const0> ;
  assign icap_o[18] = \<const0> ;
  assign icap_o[17] = \<const0> ;
  assign icap_o[16] = \<const0> ;
  assign icap_o[15] = \<const0> ;
  assign icap_o[14] = \<const0> ;
  assign icap_o[13] = \<const0> ;
  assign icap_o[12] = \<const0> ;
  assign icap_o[11] = \<const0> ;
  assign icap_o[10] = \<const0> ;
  assign icap_o[9] = \<const0> ;
  assign icap_o[8] = \<const0> ;
  assign icap_o[7] = \<const0> ;
  assign icap_o[6] = \<const0> ;
  assign icap_o[5] = \<const0> ;
  assign icap_o[4] = \<const0> ;
  assign icap_o[3] = \<const0> ;
  assign icap_o[2] = \<const0> ;
  assign icap_o[1] = \<const0> ;
  assign icap_o[0] = \<const0> ;
  assign int_dclk_out = \<const0> ;
  assign int_mmcm_lock_out = \<const0> ;
  assign int_oobclk_out = \<const0> ;
  assign int_pclk_out_slave = \<const0> ;
  assign int_pipe_rxusrclk_out = \<const0> ;
  assign int_qplllock_out[1] = \<const0> ;
  assign int_qplllock_out[0] = \<const0> ;
  assign int_qplloutclk_out[1] = \<const0> ;
  assign int_qplloutclk_out[0] = \<const0> ;
  assign int_qplloutrefclk_out[1] = \<const0> ;
  assign int_qplloutrefclk_out[0] = \<const0> ;
  assign int_rxoutclk_out[0] = \<const0> ;
  assign int_userclk1_out = \<const0> ;
  assign int_userclk2_out = \<const0> ;
  assign m_axis_rx_tkeep[7] = \^m_axis_rx_tkeep [6];
  assign m_axis_rx_tkeep[6] = \^m_axis_rx_tkeep [6];
  assign m_axis_rx_tkeep[5] = \^m_axis_rx_tkeep [6];
  assign m_axis_rx_tkeep[4] = \^m_axis_rx_tkeep [6];
  assign m_axis_rx_tkeep[3] = \<const0> ;
  assign m_axis_rx_tkeep[2] = \<const0> ;
  assign m_axis_rx_tkeep[1] = \<const0> ;
  assign m_axis_rx_tkeep[0] = \<const0> ;
  assign m_axis_rx_tuser[21] = \^m_axis_rx_tuser [21];
  assign m_axis_rx_tuser[20] = \<const0> ;
  assign m_axis_rx_tuser[19] = \^m_axis_rx_tuser [19];
  assign m_axis_rx_tuser[18] = \^m_axis_rx_tuser [17];
  assign m_axis_rx_tuser[17] = \^m_axis_rx_tuser [17];
  assign m_axis_rx_tuser[16] = \<const0> ;
  assign m_axis_rx_tuser[15] = \<const0> ;
  assign m_axis_rx_tuser[14] = \^m_axis_rx_tuser [14];
  assign m_axis_rx_tuser[13] = \<const0> ;
  assign m_axis_rx_tuser[12] = \<const0> ;
  assign m_axis_rx_tuser[11] = \<const0> ;
  assign m_axis_rx_tuser[10] = \<const0> ;
  assign m_axis_rx_tuser[9] = \<const0> ;
  assign m_axis_rx_tuser[8:0] = \^m_axis_rx_tuser [8:0];
  assign pipe_cpll_lock[0] = \<const0> ;
  assign pipe_debug[31] = \<const0> ;
  assign pipe_debug[30] = \<const0> ;
  assign pipe_debug[29] = \<const0> ;
  assign pipe_debug[28] = \<const0> ;
  assign pipe_debug[27] = \<const0> ;
  assign pipe_debug[26] = \<const0> ;
  assign pipe_debug[25] = \<const0> ;
  assign pipe_debug[24] = \<const0> ;
  assign pipe_debug[23] = \<const0> ;
  assign pipe_debug[22] = \<const0> ;
  assign pipe_debug[21] = \<const0> ;
  assign pipe_debug[20] = \<const0> ;
  assign pipe_debug[19] = \<const0> ;
  assign pipe_debug[18] = \<const0> ;
  assign pipe_debug[17] = \<const0> ;
  assign pipe_debug[16] = \<const0> ;
  assign pipe_debug[15] = \<const0> ;
  assign pipe_debug[14] = \<const0> ;
  assign pipe_debug[13] = \<const0> ;
  assign pipe_debug[12] = \<const0> ;
  assign pipe_debug[11] = \<const0> ;
  assign pipe_debug[10] = \<const0> ;
  assign pipe_debug[9] = \<const0> ;
  assign pipe_debug[8] = \<const0> ;
  assign pipe_debug[7] = \<const0> ;
  assign pipe_debug[6] = \<const0> ;
  assign pipe_debug[5] = \<const0> ;
  assign pipe_debug[4] = \<const0> ;
  assign pipe_debug[3] = \<const0> ;
  assign pipe_debug[2] = \<const0> ;
  assign pipe_debug[1] = \<const0> ;
  assign pipe_debug[0] = \<const0> ;
  assign pipe_debug_0[0] = \<const0> ;
  assign pipe_debug_1[0] = \<const0> ;
  assign pipe_debug_2[0] = \<const0> ;
  assign pipe_debug_3[0] = \<const0> ;
  assign pipe_debug_4[0] = \<const0> ;
  assign pipe_debug_5[0] = \<const0> ;
  assign pipe_debug_6[0] = \<const0> ;
  assign pipe_debug_7[0] = \<const0> ;
  assign pipe_debug_8[0] = \<const0> ;
  assign pipe_debug_9[0] = \<const0> ;
  assign pipe_dmonitorout[14] = \<const0> ;
  assign pipe_dmonitorout[13] = \<const0> ;
  assign pipe_dmonitorout[12] = \<const0> ;
  assign pipe_dmonitorout[11] = \<const0> ;
  assign pipe_dmonitorout[10] = \<const0> ;
  assign pipe_dmonitorout[9] = \<const0> ;
  assign pipe_dmonitorout[8] = \<const0> ;
  assign pipe_dmonitorout[7] = \<const0> ;
  assign pipe_dmonitorout[6] = \<const0> ;
  assign pipe_dmonitorout[5] = \<const0> ;
  assign pipe_dmonitorout[4] = \<const0> ;
  assign pipe_dmonitorout[3] = \<const0> ;
  assign pipe_dmonitorout[2] = \<const0> ;
  assign pipe_dmonitorout[1] = \<const0> ;
  assign pipe_dmonitorout[0] = \<const0> ;
  assign pipe_drp_fsm[6] = \<const0> ;
  assign pipe_drp_fsm[5] = \<const0> ;
  assign pipe_drp_fsm[4] = \<const0> ;
  assign pipe_drp_fsm[3] = \<const0> ;
  assign pipe_drp_fsm[2] = \<const0> ;
  assign pipe_drp_fsm[1] = \<const0> ;
  assign pipe_drp_fsm[0] = \<const0> ;
  assign pipe_eyescandataerror[0] = \<const0> ;
  assign pipe_gen3_out = \<const0> ;
  assign pipe_qpll_lock[0] = \<const0> ;
  assign pipe_qrst_fsm[11] = \<const0> ;
  assign pipe_qrst_fsm[10] = \<const0> ;
  assign pipe_qrst_fsm[9] = \<const0> ;
  assign pipe_qrst_fsm[8] = \<const0> ;
  assign pipe_qrst_fsm[7] = \<const0> ;
  assign pipe_qrst_fsm[6] = \<const0> ;
  assign pipe_qrst_fsm[5] = \<const0> ;
  assign pipe_qrst_fsm[4] = \<const0> ;
  assign pipe_qrst_fsm[3] = \<const0> ;
  assign pipe_qrst_fsm[2] = \<const0> ;
  assign pipe_qrst_fsm[1] = \<const0> ;
  assign pipe_qrst_fsm[0] = \<const0> ;
  assign pipe_qrst_idle = \<const0> ;
  assign pipe_rate_fsm[4] = \<const0> ;
  assign pipe_rate_fsm[3] = \<const0> ;
  assign pipe_rate_fsm[2] = \<const0> ;
  assign pipe_rate_fsm[1] = \<const0> ;
  assign pipe_rate_fsm[0] = \<const0> ;
  assign pipe_rate_idle = \<const0> ;
  assign pipe_rst_fsm[4] = \<const0> ;
  assign pipe_rst_fsm[3] = \<const0> ;
  assign pipe_rst_fsm[2] = \<const0> ;
  assign pipe_rst_fsm[1] = \<const0> ;
  assign pipe_rst_fsm[0] = \<const0> ;
  assign pipe_rst_idle = \<const0> ;
  assign pipe_rxbufstatus[2] = \<const0> ;
  assign pipe_rxbufstatus[1] = \<const0> ;
  assign pipe_rxbufstatus[0] = \<const0> ;
  assign pipe_rxcommadet[0] = \<const0> ;
  assign pipe_rxdisperr[7] = \<const0> ;
  assign pipe_rxdisperr[6] = \<const0> ;
  assign pipe_rxdisperr[5] = \<const0> ;
  assign pipe_rxdisperr[4] = \<const0> ;
  assign pipe_rxdisperr[3] = \<const0> ;
  assign pipe_rxdisperr[2] = \<const0> ;
  assign pipe_rxdisperr[1] = \<const0> ;
  assign pipe_rxdisperr[0] = \<const0> ;
  assign pipe_rxdlysresetdone[0] = \<const0> ;
  assign pipe_rxnotintable[7] = \<const0> ;
  assign pipe_rxnotintable[6] = \<const0> ;
  assign pipe_rxnotintable[5] = \<const0> ;
  assign pipe_rxnotintable[4] = \<const0> ;
  assign pipe_rxnotintable[3] = \<const0> ;
  assign pipe_rxnotintable[2] = \<const0> ;
  assign pipe_rxnotintable[1] = \<const0> ;
  assign pipe_rxnotintable[0] = \<const0> ;
  assign pipe_rxphaligndone[0] = \<const0> ;
  assign pipe_rxpmaresetdone[0] = \<const0> ;
  assign pipe_rxprbserr[0] = \<const0> ;
  assign pipe_rxstatus[2] = \<const0> ;
  assign pipe_rxstatus[1] = \<const0> ;
  assign pipe_rxstatus[0] = \<const0> ;
  assign pipe_rxsyncdone[0] = \<const0> ;
  assign pipe_sync_fsm_rx[6] = \<const0> ;
  assign pipe_sync_fsm_rx[5] = \<const0> ;
  assign pipe_sync_fsm_rx[4] = \<const0> ;
  assign pipe_sync_fsm_rx[3] = \<const0> ;
  assign pipe_sync_fsm_rx[2] = \<const0> ;
  assign pipe_sync_fsm_rx[1] = \<const0> ;
  assign pipe_sync_fsm_rx[0] = \<const0> ;
  assign pipe_sync_fsm_tx[5] = \<const0> ;
  assign pipe_sync_fsm_tx[4] = \<const0> ;
  assign pipe_sync_fsm_tx[3] = \<const0> ;
  assign pipe_sync_fsm_tx[2] = \<const0> ;
  assign pipe_sync_fsm_tx[1] = \<const0> ;
  assign pipe_sync_fsm_tx[0] = \<const0> ;
  assign pipe_tx_0_sigs[24] = \<const0> ;
  assign pipe_tx_0_sigs[23] = \<const0> ;
  assign pipe_tx_0_sigs[22] = \<const0> ;
  assign pipe_tx_0_sigs[21] = \<const0> ;
  assign pipe_tx_0_sigs[20] = \<const0> ;
  assign pipe_tx_0_sigs[19] = \<const0> ;
  assign pipe_tx_0_sigs[18] = \<const0> ;
  assign pipe_tx_0_sigs[17] = \<const0> ;
  assign pipe_tx_0_sigs[16] = \<const0> ;
  assign pipe_tx_0_sigs[15] = \<const0> ;
  assign pipe_tx_0_sigs[14] = \<const0> ;
  assign pipe_tx_0_sigs[13] = \<const0> ;
  assign pipe_tx_0_sigs[12] = \<const0> ;
  assign pipe_tx_0_sigs[11] = \<const0> ;
  assign pipe_tx_0_sigs[10] = \<const0> ;
  assign pipe_tx_0_sigs[9] = \<const0> ;
  assign pipe_tx_0_sigs[8] = \<const0> ;
  assign pipe_tx_0_sigs[7] = \<const0> ;
  assign pipe_tx_0_sigs[6] = \<const0> ;
  assign pipe_tx_0_sigs[5] = \<const0> ;
  assign pipe_tx_0_sigs[4] = \<const0> ;
  assign pipe_tx_0_sigs[3] = \<const0> ;
  assign pipe_tx_0_sigs[2] = \<const0> ;
  assign pipe_tx_0_sigs[1] = \<const0> ;
  assign pipe_tx_0_sigs[0] = \<const0> ;
  assign pipe_tx_1_sigs[24] = \<const0> ;
  assign pipe_tx_1_sigs[23] = \<const0> ;
  assign pipe_tx_1_sigs[22] = \<const0> ;
  assign pipe_tx_1_sigs[21] = \<const0> ;
  assign pipe_tx_1_sigs[20] = \<const0> ;
  assign pipe_tx_1_sigs[19] = \<const0> ;
  assign pipe_tx_1_sigs[18] = \<const0> ;
  assign pipe_tx_1_sigs[17] = \<const0> ;
  assign pipe_tx_1_sigs[16] = \<const0> ;
  assign pipe_tx_1_sigs[15] = \<const0> ;
  assign pipe_tx_1_sigs[14] = \<const0> ;
  assign pipe_tx_1_sigs[13] = \<const0> ;
  assign pipe_tx_1_sigs[12] = \<const0> ;
  assign pipe_tx_1_sigs[11] = \<const0> ;
  assign pipe_tx_1_sigs[10] = \<const0> ;
  assign pipe_tx_1_sigs[9] = \<const0> ;
  assign pipe_tx_1_sigs[8] = \<const0> ;
  assign pipe_tx_1_sigs[7] = \<const0> ;
  assign pipe_tx_1_sigs[6] = \<const0> ;
  assign pipe_tx_1_sigs[5] = \<const0> ;
  assign pipe_tx_1_sigs[4] = \<const0> ;
  assign pipe_tx_1_sigs[3] = \<const0> ;
  assign pipe_tx_1_sigs[2] = \<const0> ;
  assign pipe_tx_1_sigs[1] = \<const0> ;
  assign pipe_tx_1_sigs[0] = \<const0> ;
  assign pipe_tx_2_sigs[24] = \<const0> ;
  assign pipe_tx_2_sigs[23] = \<const0> ;
  assign pipe_tx_2_sigs[22] = \<const0> ;
  assign pipe_tx_2_sigs[21] = \<const0> ;
  assign pipe_tx_2_sigs[20] = \<const0> ;
  assign pipe_tx_2_sigs[19] = \<const0> ;
  assign pipe_tx_2_sigs[18] = \<const0> ;
  assign pipe_tx_2_sigs[17] = \<const0> ;
  assign pipe_tx_2_sigs[16] = \<const0> ;
  assign pipe_tx_2_sigs[15] = \<const0> ;
  assign pipe_tx_2_sigs[14] = \<const0> ;
  assign pipe_tx_2_sigs[13] = \<const0> ;
  assign pipe_tx_2_sigs[12] = \<const0> ;
  assign pipe_tx_2_sigs[11] = \<const0> ;
  assign pipe_tx_2_sigs[10] = \<const0> ;
  assign pipe_tx_2_sigs[9] = \<const0> ;
  assign pipe_tx_2_sigs[8] = \<const0> ;
  assign pipe_tx_2_sigs[7] = \<const0> ;
  assign pipe_tx_2_sigs[6] = \<const0> ;
  assign pipe_tx_2_sigs[5] = \<const0> ;
  assign pipe_tx_2_sigs[4] = \<const0> ;
  assign pipe_tx_2_sigs[3] = \<const0> ;
  assign pipe_tx_2_sigs[2] = \<const0> ;
  assign pipe_tx_2_sigs[1] = \<const0> ;
  assign pipe_tx_2_sigs[0] = \<const0> ;
  assign pipe_tx_3_sigs[24] = \<const0> ;
  assign pipe_tx_3_sigs[23] = \<const0> ;
  assign pipe_tx_3_sigs[22] = \<const0> ;
  assign pipe_tx_3_sigs[21] = \<const0> ;
  assign pipe_tx_3_sigs[20] = \<const0> ;
  assign pipe_tx_3_sigs[19] = \<const0> ;
  assign pipe_tx_3_sigs[18] = \<const0> ;
  assign pipe_tx_3_sigs[17] = \<const0> ;
  assign pipe_tx_3_sigs[16] = \<const0> ;
  assign pipe_tx_3_sigs[15] = \<const0> ;
  assign pipe_tx_3_sigs[14] = \<const0> ;
  assign pipe_tx_3_sigs[13] = \<const0> ;
  assign pipe_tx_3_sigs[12] = \<const0> ;
  assign pipe_tx_3_sigs[11] = \<const0> ;
  assign pipe_tx_3_sigs[10] = \<const0> ;
  assign pipe_tx_3_sigs[9] = \<const0> ;
  assign pipe_tx_3_sigs[8] = \<const0> ;
  assign pipe_tx_3_sigs[7] = \<const0> ;
  assign pipe_tx_3_sigs[6] = \<const0> ;
  assign pipe_tx_3_sigs[5] = \<const0> ;
  assign pipe_tx_3_sigs[4] = \<const0> ;
  assign pipe_tx_3_sigs[3] = \<const0> ;
  assign pipe_tx_3_sigs[2] = \<const0> ;
  assign pipe_tx_3_sigs[1] = \<const0> ;
  assign pipe_tx_3_sigs[0] = \<const0> ;
  assign pipe_tx_4_sigs[24] = \<const0> ;
  assign pipe_tx_4_sigs[23] = \<const0> ;
  assign pipe_tx_4_sigs[22] = \<const0> ;
  assign pipe_tx_4_sigs[21] = \<const0> ;
  assign pipe_tx_4_sigs[20] = \<const0> ;
  assign pipe_tx_4_sigs[19] = \<const0> ;
  assign pipe_tx_4_sigs[18] = \<const0> ;
  assign pipe_tx_4_sigs[17] = \<const0> ;
  assign pipe_tx_4_sigs[16] = \<const0> ;
  assign pipe_tx_4_sigs[15] = \<const0> ;
  assign pipe_tx_4_sigs[14] = \<const0> ;
  assign pipe_tx_4_sigs[13] = \<const0> ;
  assign pipe_tx_4_sigs[12] = \<const0> ;
  assign pipe_tx_4_sigs[11] = \<const0> ;
  assign pipe_tx_4_sigs[10] = \<const0> ;
  assign pipe_tx_4_sigs[9] = \<const0> ;
  assign pipe_tx_4_sigs[8] = \<const0> ;
  assign pipe_tx_4_sigs[7] = \<const0> ;
  assign pipe_tx_4_sigs[6] = \<const0> ;
  assign pipe_tx_4_sigs[5] = \<const0> ;
  assign pipe_tx_4_sigs[4] = \<const0> ;
  assign pipe_tx_4_sigs[3] = \<const0> ;
  assign pipe_tx_4_sigs[2] = \<const0> ;
  assign pipe_tx_4_sigs[1] = \<const0> ;
  assign pipe_tx_4_sigs[0] = \<const0> ;
  assign pipe_tx_5_sigs[24] = \<const0> ;
  assign pipe_tx_5_sigs[23] = \<const0> ;
  assign pipe_tx_5_sigs[22] = \<const0> ;
  assign pipe_tx_5_sigs[21] = \<const0> ;
  assign pipe_tx_5_sigs[20] = \<const0> ;
  assign pipe_tx_5_sigs[19] = \<const0> ;
  assign pipe_tx_5_sigs[18] = \<const0> ;
  assign pipe_tx_5_sigs[17] = \<const0> ;
  assign pipe_tx_5_sigs[16] = \<const0> ;
  assign pipe_tx_5_sigs[15] = \<const0> ;
  assign pipe_tx_5_sigs[14] = \<const0> ;
  assign pipe_tx_5_sigs[13] = \<const0> ;
  assign pipe_tx_5_sigs[12] = \<const0> ;
  assign pipe_tx_5_sigs[11] = \<const0> ;
  assign pipe_tx_5_sigs[10] = \<const0> ;
  assign pipe_tx_5_sigs[9] = \<const0> ;
  assign pipe_tx_5_sigs[8] = \<const0> ;
  assign pipe_tx_5_sigs[7] = \<const0> ;
  assign pipe_tx_5_sigs[6] = \<const0> ;
  assign pipe_tx_5_sigs[5] = \<const0> ;
  assign pipe_tx_5_sigs[4] = \<const0> ;
  assign pipe_tx_5_sigs[3] = \<const0> ;
  assign pipe_tx_5_sigs[2] = \<const0> ;
  assign pipe_tx_5_sigs[1] = \<const0> ;
  assign pipe_tx_5_sigs[0] = \<const0> ;
  assign pipe_tx_6_sigs[24] = \<const0> ;
  assign pipe_tx_6_sigs[23] = \<const0> ;
  assign pipe_tx_6_sigs[22] = \<const0> ;
  assign pipe_tx_6_sigs[21] = \<const0> ;
  assign pipe_tx_6_sigs[20] = \<const0> ;
  assign pipe_tx_6_sigs[19] = \<const0> ;
  assign pipe_tx_6_sigs[18] = \<const0> ;
  assign pipe_tx_6_sigs[17] = \<const0> ;
  assign pipe_tx_6_sigs[16] = \<const0> ;
  assign pipe_tx_6_sigs[15] = \<const0> ;
  assign pipe_tx_6_sigs[14] = \<const0> ;
  assign pipe_tx_6_sigs[13] = \<const0> ;
  assign pipe_tx_6_sigs[12] = \<const0> ;
  assign pipe_tx_6_sigs[11] = \<const0> ;
  assign pipe_tx_6_sigs[10] = \<const0> ;
  assign pipe_tx_6_sigs[9] = \<const0> ;
  assign pipe_tx_6_sigs[8] = \<const0> ;
  assign pipe_tx_6_sigs[7] = \<const0> ;
  assign pipe_tx_6_sigs[6] = \<const0> ;
  assign pipe_tx_6_sigs[5] = \<const0> ;
  assign pipe_tx_6_sigs[4] = \<const0> ;
  assign pipe_tx_6_sigs[3] = \<const0> ;
  assign pipe_tx_6_sigs[2] = \<const0> ;
  assign pipe_tx_6_sigs[1] = \<const0> ;
  assign pipe_tx_6_sigs[0] = \<const0> ;
  assign pipe_tx_7_sigs[24] = \<const0> ;
  assign pipe_tx_7_sigs[23] = \<const0> ;
  assign pipe_tx_7_sigs[22] = \<const0> ;
  assign pipe_tx_7_sigs[21] = \<const0> ;
  assign pipe_tx_7_sigs[20] = \<const0> ;
  assign pipe_tx_7_sigs[19] = \<const0> ;
  assign pipe_tx_7_sigs[18] = \<const0> ;
  assign pipe_tx_7_sigs[17] = \<const0> ;
  assign pipe_tx_7_sigs[16] = \<const0> ;
  assign pipe_tx_7_sigs[15] = \<const0> ;
  assign pipe_tx_7_sigs[14] = \<const0> ;
  assign pipe_tx_7_sigs[13] = \<const0> ;
  assign pipe_tx_7_sigs[12] = \<const0> ;
  assign pipe_tx_7_sigs[11] = \<const0> ;
  assign pipe_tx_7_sigs[10] = \<const0> ;
  assign pipe_tx_7_sigs[9] = \<const0> ;
  assign pipe_tx_7_sigs[8] = \<const0> ;
  assign pipe_tx_7_sigs[7] = \<const0> ;
  assign pipe_tx_7_sigs[6] = \<const0> ;
  assign pipe_tx_7_sigs[5] = \<const0> ;
  assign pipe_tx_7_sigs[4] = \<const0> ;
  assign pipe_tx_7_sigs[3] = \<const0> ;
  assign pipe_tx_7_sigs[2] = \<const0> ;
  assign pipe_tx_7_sigs[1] = \<const0> ;
  assign pipe_tx_7_sigs[0] = \<const0> ;
  assign pipe_txdlysresetdone[0] = \<const0> ;
  assign pipe_txphaligndone[0] = \<const0> ;
  assign pipe_txphinitdone[0] = \<const0> ;
  assign qpll_drp_clk = \<const0> ;
  assign qpll_drp_gen3 = \<const0> ;
  assign qpll_drp_ovrd = \<const0> ;
  assign qpll_drp_rst_n = \<const0> ;
  assign qpll_drp_start = \<const0> ;
  assign qpll_qplld = \<const0> ;
  assign qpll_qpllreset[1] = \<const0> ;
  assign qpll_qpllreset[0] = \<const0> ;
  assign startup_cfgclk = \<const0> ;
  assign startup_cfgmclk = \<const0> ;
  assign startup_eos = \<const0> ;
  assign startup_preq = \<const0> ;
  assign user_app_rdy = \<const0> ;
  assign user_clk_out = pipe_userclk2_in;
  GND GND
       (.G(\<const0> ));
  pcie_7x_bridge_core_top inst
       (.cfg_aer_ecrc_check_en(cfg_aer_ecrc_check_en),
        .cfg_aer_ecrc_gen_en(cfg_aer_ecrc_gen_en),
        .cfg_aer_interrupt_msgnum(cfg_aer_interrupt_msgnum),
        .cfg_aer_rooterr_corr_err_received(cfg_aer_rooterr_corr_err_received),
        .cfg_aer_rooterr_corr_err_reporting_en(cfg_aer_rooterr_corr_err_reporting_en),
        .cfg_aer_rooterr_fatal_err_received(cfg_aer_rooterr_fatal_err_received),
        .cfg_aer_rooterr_fatal_err_reporting_en(cfg_aer_rooterr_fatal_err_reporting_en),
        .cfg_aer_rooterr_non_fatal_err_received(cfg_aer_rooterr_non_fatal_err_received),
        .cfg_aer_rooterr_non_fatal_err_reporting_en(cfg_aer_rooterr_non_fatal_err_reporting_en),
        .cfg_bridge_serr_en(cfg_bridge_serr_en),
        .cfg_bus_number(cfg_bus_number),
        .cfg_command({\^cfg_command [10],\^cfg_command [8],\^cfg_command [2:0]}),
        .cfg_dcommand(\^cfg_dcommand ),
        .cfg_dcommand2(\^cfg_dcommand2 ),
        .cfg_device_number(cfg_device_number),
        .cfg_ds_bus_number(cfg_ds_bus_number),
        .cfg_ds_device_number(cfg_ds_device_number),
        .cfg_ds_function_number(cfg_ds_function_number),
        .cfg_dsn(cfg_dsn),
        .cfg_dstatus(\^cfg_dstatus ),
        .cfg_err_aer_headerlog(cfg_err_aer_headerlog),
        .cfg_err_aer_headerlog_set(cfg_err_aer_headerlog_set),
        .cfg_err_atomic_egress_blocked(cfg_err_atomic_egress_blocked),
        .cfg_err_cor(cfg_err_cor),
        .cfg_err_cpl_abort(cfg_err_cpl_abort),
        .cfg_err_cpl_rdy(cfg_err_cpl_rdy),
        .cfg_err_cpl_timeout(cfg_err_cpl_timeout),
        .cfg_err_cpl_unexpect(cfg_err_cpl_unexpect),
        .cfg_err_ecrc(cfg_err_ecrc),
        .cfg_err_internal_cor(cfg_err_internal_cor),
        .cfg_err_internal_uncor(cfg_err_internal_uncor),
        .cfg_err_locked(cfg_err_locked),
        .cfg_err_malformed(cfg_err_malformed),
        .cfg_err_mc_blocked(cfg_err_mc_blocked),
        .cfg_err_norecovery(cfg_err_norecovery),
        .cfg_err_poisoned(cfg_err_poisoned),
        .cfg_err_posted(cfg_err_posted),
        .cfg_err_tlp_cpl_header(cfg_err_tlp_cpl_header),
        .cfg_err_ur(cfg_err_ur),
        .cfg_function_number(cfg_function_number),
        .cfg_interrupt(cfg_interrupt),
        .cfg_interrupt_assert(cfg_interrupt_assert),
        .cfg_interrupt_di(cfg_interrupt_di),
        .cfg_interrupt_do(cfg_interrupt_do),
        .cfg_interrupt_mmenable(cfg_interrupt_mmenable),
        .cfg_interrupt_msienable(cfg_interrupt_msienable),
        .cfg_interrupt_msixenable(cfg_interrupt_msixenable),
        .cfg_interrupt_msixfm(cfg_interrupt_msixfm),
        .cfg_interrupt_rdy(cfg_interrupt_rdy),
        .cfg_interrupt_stat(cfg_interrupt_stat),
        .cfg_lcommand({\^cfg_lcommand [11:3],\^cfg_lcommand [1:0]}),
        .cfg_lstatus({\^cfg_lstatus [15:13],\^cfg_lstatus [11],\^cfg_lstatus [7:4],\^cfg_lstatus [1:0]}),
        .cfg_mgmt_byte_en(cfg_mgmt_byte_en),
        .cfg_mgmt_di(cfg_mgmt_di),
        .cfg_mgmt_do(cfg_mgmt_do),
        .cfg_mgmt_dwaddr(cfg_mgmt_dwaddr),
        .cfg_mgmt_rd_en(cfg_mgmt_rd_en),
        .cfg_mgmt_rd_wr_done(cfg_mgmt_rd_wr_done),
        .cfg_mgmt_wr_en(cfg_mgmt_wr_en),
        .cfg_mgmt_wr_readonly(cfg_mgmt_wr_readonly),
        .cfg_mgmt_wr_rw1c_as_rw(cfg_mgmt_wr_rw1c_as_rw),
        .cfg_msg_data(cfg_msg_data),
        .cfg_msg_received(cfg_msg_received),
        .cfg_msg_received_assert_int_a(cfg_msg_received_assert_int_a),
        .cfg_msg_received_assert_int_b(cfg_msg_received_assert_int_b),
        .cfg_msg_received_assert_int_c(cfg_msg_received_assert_int_c),
        .cfg_msg_received_assert_int_d(cfg_msg_received_assert_int_d),
        .cfg_msg_received_deassert_int_a(cfg_msg_received_deassert_int_a),
        .cfg_msg_received_deassert_int_b(cfg_msg_received_deassert_int_b),
        .cfg_msg_received_deassert_int_c(cfg_msg_received_deassert_int_c),
        .cfg_msg_received_deassert_int_d(cfg_msg_received_deassert_int_d),
        .cfg_msg_received_err_cor(cfg_msg_received_err_cor),
        .cfg_msg_received_err_fatal(cfg_msg_received_err_fatal),
        .cfg_msg_received_err_non_fatal(cfg_msg_received_err_non_fatal),
        .cfg_msg_received_pm_as_nak(cfg_msg_received_pm_as_nak),
        .cfg_msg_received_pm_pme(cfg_msg_received_pm_pme),
        .cfg_msg_received_pme_to_ack(cfg_msg_received_pme_to_ack),
        .cfg_msg_received_setslotpowerlimit(cfg_msg_received_setslotpowerlimit),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pciecap_interrupt_msgnum(cfg_pciecap_interrupt_msgnum),
        .cfg_pm_force_state(cfg_pm_force_state),
        .cfg_pm_force_state_en(cfg_pm_force_state_en),
        .cfg_pm_halt_aspm_l0s(cfg_pm_halt_aspm_l0s),
        .cfg_pm_halt_aspm_l1(cfg_pm_halt_aspm_l1),
        .cfg_pm_wake(cfg_pm_wake),
        .cfg_pmcsr_pme_en(cfg_pmcsr_pme_en),
        .cfg_pmcsr_pme_status(cfg_pmcsr_pme_status),
        .cfg_pmcsr_powerstate(cfg_pmcsr_powerstate),
        .cfg_received_func_lvl_rst(cfg_received_func_lvl_rst),
        .cfg_root_control_pme_int_en(cfg_root_control_pme_int_en),
        .cfg_root_control_syserr_corr_err_en(cfg_root_control_syserr_corr_err_en),
        .cfg_root_control_syserr_fatal_err_en(cfg_root_control_syserr_fatal_err_en),
        .cfg_root_control_syserr_non_fatal_err_en(cfg_root_control_syserr_non_fatal_err_en),
        .cfg_slot_control_electromech_il_ctl_pulse(cfg_slot_control_electromech_il_ctl_pulse),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_trn_pending(cfg_trn_pending),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .cfg_vc_tcvc_map(cfg_vc_tcvc_map),
        .fc_cpld(fc_cpld),
        .fc_cplh(fc_cplh),
        .fc_npd(fc_npd),
        .fc_nph(fc_nph),
        .fc_pd(fc_pd),
        .fc_ph(fc_ph),
        .fc_sel(fc_sel),
        .m_axis_rx_tdata(m_axis_rx_tdata),
        .m_axis_rx_tkeep(\^m_axis_rx_tkeep ),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser({\^m_axis_rx_tuser [21],\^m_axis_rx_tuser [19],\^m_axis_rx_tuser [17],\^m_axis_rx_tuser [14],\^m_axis_rx_tuser [8:0]}),
        .m_axis_rx_tvalid(m_axis_rx_tvalid),
        .pci_exp_rxn(pci_exp_rxn),
        .pci_exp_rxp(pci_exp_rxp),
        .pci_exp_txn(pci_exp_txn),
        .pci_exp_txp(pci_exp_txp),
        .pcie_drp_addr(pcie_drp_addr),
        .pcie_drp_clk(pcie_drp_clk),
        .pcie_drp_di(pcie_drp_di),
        .pcie_drp_do(pcie_drp_do),
        .pcie_drp_en(pcie_drp_en),
        .pcie_drp_rdy(pcie_drp_rdy),
        .pcie_drp_we(pcie_drp_we),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_oobclk_in(pipe_oobclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .pipe_rxoutclk_out(pipe_rxoutclk_out),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_txoutclk_out(pipe_txoutclk_out),
        .pipe_userclk1_in(pipe_userclk1_in),
        .pipe_userclk2_in(pipe_userclk2_in),
        .pl_directed_change_done(pl_directed_change_done),
        .pl_directed_link_auton(pl_directed_link_auton),
        .pl_directed_link_change(pl_directed_link_change),
        .pl_directed_link_speed(pl_directed_link_speed),
        .pl_directed_link_width(pl_directed_link_width),
        .pl_downstream_deemph_source(pl_downstream_deemph_source),
        .pl_initial_link_width(pl_initial_link_width),
        .pl_lane_reversal_mode(pl_lane_reversal_mode),
        .pl_link_gen2_cap(pl_link_gen2_cap),
        .pl_link_partner_gen2_supported(pl_link_partner_gen2_supported),
        .pl_link_upcfg_cap(pl_link_upcfg_cap),
        .pl_ltssm_state(pl_ltssm_state),
        .pl_phy_lnk_up(pl_phy_lnk_up),
        .pl_received_hot_rst(pl_received_hot_rst),
        .pl_rx_pm_state(pl_rx_pm_state),
        .pl_sel_lnk_rate(pl_sel_lnk_rate),
        .pl_sel_lnk_width(pl_sel_lnk_width),
        .pl_transmit_hot_rst(pl_transmit_hot_rst),
        .pl_tx_pm_state(pl_tx_pm_state),
        .pl_upstream_prefer_deemph(pl_upstream_prefer_deemph),
        .rx_np_ok(rx_np_ok),
        .rx_np_req(rx_np_req),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep(s_axis_tx_tkeep[7]),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tready(s_axis_tx_tready),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .sys_clk(sys_clk),
        .sys_rst_n(sys_rst_n),
        .tx_buf_av(tx_buf_av),
        .tx_cfg_gnt(tx_cfg_gnt),
        .tx_cfg_req(tx_cfg_req),
        .tx_err_drop(tx_err_drop),
        .user_lnk_up(user_lnk_up),
        .user_reset_out(user_reset_out));
endmodule

module pcie_7x_bridge_pcie_7x
   (user_reset_int_reg,
    src_in,
    cfg_mgmt_rd_wr_done,
    cfg_err_aer_headerlog_set,
    cfg_err_cpl_rdy,
    cfg_interrupt_rdy,
    E,
    cfg_msg_received,
    cfg_received_func_lvl_rst,
    trn_in_packet_reg,
    trn_reof,
    trn_rsof,
    trn_rsrc_dsc,
    pcie_block_i_0,
    cfg_pcie_link_state,
    dsc_detect,
    rsrc_rdy_filtered,
    trn_rsrc_dsc_prev0,
    tcfg_req_trig,
    trn_tcfg_req,
    pcie_block_i_1,
    trn_tbuf_av,
    tbuf_av_min_trig,
    pcie_block_i_2,
    trn_tdst_rdy,
    cfg_aer_ecrc_check_en,
    cfg_aer_ecrc_gen_en,
    cfg_aer_rooterr_corr_err_received,
    cfg_aer_rooterr_corr_err_reporting_en,
    cfg_aer_rooterr_fatal_err_received,
    cfg_aer_rooterr_fatal_err_reporting_en,
    cfg_aer_rooterr_non_fatal_err_received,
    cfg_aer_rooterr_non_fatal_err_reporting_en,
    cfg_bridge_serr_en,
    cfg_command,
    cfg_dcommand2,
    cfg_dcommand,
    cfg_dstatus,
    cfg_interrupt_msienable,
    cfg_interrupt_msixenable,
    cfg_interrupt_msixfm,
    cfg_lcommand,
    cfg_lstatus,
    cfg_msg_received_assert_int_a,
    cfg_msg_received_assert_int_b,
    cfg_msg_received_assert_int_c,
    cfg_msg_received_assert_int_d,
    cfg_msg_received_deassert_int_a,
    cfg_msg_received_deassert_int_b,
    cfg_msg_received_deassert_int_c,
    cfg_msg_received_deassert_int_d,
    cfg_msg_received_err_cor,
    cfg_msg_received_err_fatal,
    cfg_msg_received_err_non_fatal,
    cfg_msg_received_pm_as_nak,
    cfg_to_turnoff,
    cfg_msg_received_pme_to_ack,
    cfg_msg_received_pm_pme,
    cfg_msg_received_setslotpowerlimit,
    cfg_pmcsr_pme_en,
    cfg_pmcsr_pme_status,
    cfg_root_control_pme_int_en,
    cfg_root_control_syserr_corr_err_en,
    cfg_root_control_syserr_fatal_err_en,
    cfg_root_control_syserr_non_fatal_err_en,
    cfg_slot_control_electromech_il_ctl_pulse,
    pcie_drp_rdy,
    pipe_rx0_polarity,
    pipe_tx0_compliance,
    pipe_tx0_elec_idle,
    pipe_tx_deemph,
    pipe_tx_rate,
    pipe_tx_rcvr_det,
    pl_directed_change_done,
    pl_link_gen2_cap,
    pl_link_partner_gen2_supported,
    pl_link_upcfg_cap,
    pl_received_hot_rst,
    pl_sel_lnk_rate,
    trn_lnk_up,
    trn_recrc_err,
    trn_rerrfwd,
    tx_err_drop,
    fc_cpld,
    fc_npd,
    fc_pd,
    pcie_block_i_3,
    cfg_msg_data,
    pcie_drp_do,
    pipe_tx0_data,
    cfg_pmcsr_powerstate,
    pipe_tx0_char_is_k,
    pipe_tx0_powerdown,
    pl_lane_reversal_mode,
    pl_rx_pm_state,
    pl_sel_lnk_width,
    pcie_block_i_4,
    cfg_interrupt_mmenable,
    pipe_tx_margin,
    pl_initial_link_width,
    pl_tx_pm_state,
    cfg_mgmt_do,
    pl_ltssm_state,
    cfg_vc_tcvc_map,
    cfg_interrupt_do,
    fc_cplh,
    fc_nph,
    fc_ph,
    trn_rbar_hit,
    bridge_reset_int,
    pl_phy_lnk_up,
    cfg_trn_pending,
    trn_in_packet,
    trn_rdst_rdy,
    ppm_L1_trig,
    ppm_L1_thrtl,
    cfg_mgmt_wr_rw1c_as_rw,
    cfg_mgmt_wr_readonly,
    cfg_mgmt_wr_en,
    cfg_mgmt_rd_en,
    cfg_err_malformed,
    cfg_err_cor,
    cfg_err_ur,
    cfg_err_ecrc,
    cfg_err_cpl_timeout,
    cfg_err_cpl_abort,
    cfg_err_cpl_unexpect,
    cfg_err_poisoned,
    cfg_err_atomic_egress_blocked,
    cfg_err_mc_blocked,
    cfg_err_internal_uncor,
    cfg_err_internal_cor,
    cfg_err_posted,
    cfg_err_locked,
    cfg_err_norecovery,
    cfg_interrupt,
    cfg_interrupt_assert,
    cfg_interrupt_stat,
    cfg_pm_halt_aspm_l0s,
    cfg_pm_halt_aspm_l1,
    cfg_pm_force_state_en,
    cfg_pm_wake,
    trn_rsrc_dsc_d,
    reg_dsc_detect,
    reg_tcfg_gnt,
    lnk_up_thrtl,
    out,
    pipe_userclk1_in,
    cfg_pm_turnoff_ok_n,
    pcie_drp_clk,
    pcie_drp_en,
    pcie_drp_we,
    pipe_pclk_in,
    pipe_rx0_chanisaligned,
    pipe_rx0_elec_idle,
    pipe_rx0_phy_status,
    pipe_rx0_valid,
    pl_directed_link_auton,
    pl_directed_link_speed,
    pl_downstream_deemph_source,
    pl_transmit_hot_rst,
    pl_upstream_prefer_deemph,
    sys_rst_n,
    rx_np_ok,
    rx_np_req,
    trn_tcfg_gnt,
    pcie_block_i_5,
    trn_teof,
    trn_tsof,
    trn_tsrc_rdy,
    pipe_userclk2_in,
    cfg_err_aer_headerlog,
    trn_td,
    pcie_drp_di,
    pipe_rx0_data,
    cfg_pm_force_state,
    pipe_rx0_char_is_k,
    pl_directed_link_change,
    pl_directed_link_width,
    trn_trem,
    cfg_ds_function_number,
    pipe_rx0_status,
    fc_sel,
    cfg_mgmt_di,
    cfg_mgmt_byte_en_n,
    cfg_err_tlp_cpl_header,
    cfg_aer_interrupt_msgnum,
    cfg_ds_device_number,
    cfg_pciecap_interrupt_msgnum,
    cfg_dsn,
    cfg_ds_bus_number,
    cfg_interrupt_di,
    pcie_drp_addr,
    cfg_mgmt_dwaddr);
  output user_reset_int_reg;
  output src_in;
  output cfg_mgmt_rd_wr_done;
  output cfg_err_aer_headerlog_set;
  output cfg_err_cpl_rdy;
  output cfg_interrupt_rdy;
  output [0:0]E;
  output cfg_msg_received;
  output cfg_received_func_lvl_rst;
  output trn_in_packet_reg;
  output trn_reof;
  output trn_rsof;
  output trn_rsrc_dsc;
  output pcie_block_i_0;
  output [2:0]cfg_pcie_link_state;
  output dsc_detect;
  output rsrc_rdy_filtered;
  output trn_rsrc_dsc_prev0;
  output tcfg_req_trig;
  output trn_tcfg_req;
  output pcie_block_i_1;
  output [5:0]trn_tbuf_av;
  output tbuf_av_min_trig;
  output pcie_block_i_2;
  output trn_tdst_rdy;
  output cfg_aer_ecrc_check_en;
  output cfg_aer_ecrc_gen_en;
  output cfg_aer_rooterr_corr_err_received;
  output cfg_aer_rooterr_corr_err_reporting_en;
  output cfg_aer_rooterr_fatal_err_received;
  output cfg_aer_rooterr_fatal_err_reporting_en;
  output cfg_aer_rooterr_non_fatal_err_received;
  output cfg_aer_rooterr_non_fatal_err_reporting_en;
  output cfg_bridge_serr_en;
  output [4:0]cfg_command;
  output [11:0]cfg_dcommand2;
  output [14:0]cfg_dcommand;
  output [3:0]cfg_dstatus;
  output cfg_interrupt_msienable;
  output cfg_interrupt_msixenable;
  output cfg_interrupt_msixfm;
  output [10:0]cfg_lcommand;
  output [9:0]cfg_lstatus;
  output cfg_msg_received_assert_int_a;
  output cfg_msg_received_assert_int_b;
  output cfg_msg_received_assert_int_c;
  output cfg_msg_received_assert_int_d;
  output cfg_msg_received_deassert_int_a;
  output cfg_msg_received_deassert_int_b;
  output cfg_msg_received_deassert_int_c;
  output cfg_msg_received_deassert_int_d;
  output cfg_msg_received_err_cor;
  output cfg_msg_received_err_fatal;
  output cfg_msg_received_err_non_fatal;
  output cfg_msg_received_pm_as_nak;
  output cfg_to_turnoff;
  output cfg_msg_received_pme_to_ack;
  output cfg_msg_received_pm_pme;
  output cfg_msg_received_setslotpowerlimit;
  output cfg_pmcsr_pme_en;
  output cfg_pmcsr_pme_status;
  output cfg_root_control_pme_int_en;
  output cfg_root_control_syserr_corr_err_en;
  output cfg_root_control_syserr_fatal_err_en;
  output cfg_root_control_syserr_non_fatal_err_en;
  output cfg_slot_control_electromech_il_ctl_pulse;
  output pcie_drp_rdy;
  output pipe_rx0_polarity;
  output pipe_tx0_compliance;
  output pipe_tx0_elec_idle;
  output pipe_tx_deemph;
  output pipe_tx_rate;
  output pipe_tx_rcvr_det;
  output pl_directed_change_done;
  output pl_link_gen2_cap;
  output pl_link_partner_gen2_supported;
  output pl_link_upcfg_cap;
  output pl_received_hot_rst;
  output pl_sel_lnk_rate;
  output trn_lnk_up;
  output trn_recrc_err;
  output trn_rerrfwd;
  output tx_err_drop;
  output [11:0]fc_cpld;
  output [11:0]fc_npd;
  output [11:0]fc_pd;
  output [63:0]pcie_block_i_3;
  output [15:0]cfg_msg_data;
  output [15:0]pcie_drp_do;
  output [15:0]pipe_tx0_data;
  output [1:0]cfg_pmcsr_powerstate;
  output [1:0]pipe_tx0_char_is_k;
  output [1:0]pipe_tx0_powerdown;
  output [1:0]pl_lane_reversal_mode;
  output [1:0]pl_rx_pm_state;
  output [1:0]pl_sel_lnk_width;
  output [0:0]pcie_block_i_4;
  output [2:0]cfg_interrupt_mmenable;
  output [2:0]pipe_tx_margin;
  output [2:0]pl_initial_link_width;
  output [2:0]pl_tx_pm_state;
  output [31:0]cfg_mgmt_do;
  output [5:0]pl_ltssm_state;
  output [6:0]cfg_vc_tcvc_map;
  output [7:0]cfg_interrupt_do;
  output [7:0]fc_cplh;
  output [7:0]fc_nph;
  output [7:0]fc_ph;
  output [6:0]trn_rbar_hit;
  input bridge_reset_int;
  input pl_phy_lnk_up;
  input cfg_trn_pending;
  input trn_in_packet;
  input trn_rdst_rdy;
  input ppm_L1_trig;
  input ppm_L1_thrtl;
  input cfg_mgmt_wr_rw1c_as_rw;
  input cfg_mgmt_wr_readonly;
  input cfg_mgmt_wr_en;
  input cfg_mgmt_rd_en;
  input cfg_err_malformed;
  input cfg_err_cor;
  input cfg_err_ur;
  input cfg_err_ecrc;
  input cfg_err_cpl_timeout;
  input cfg_err_cpl_abort;
  input cfg_err_cpl_unexpect;
  input cfg_err_poisoned;
  input cfg_err_atomic_egress_blocked;
  input cfg_err_mc_blocked;
  input cfg_err_internal_uncor;
  input cfg_err_internal_cor;
  input cfg_err_posted;
  input cfg_err_locked;
  input cfg_err_norecovery;
  input cfg_interrupt;
  input cfg_interrupt_assert;
  input cfg_interrupt_stat;
  input cfg_pm_halt_aspm_l0s;
  input cfg_pm_halt_aspm_l1;
  input cfg_pm_force_state_en;
  input cfg_pm_wake;
  input trn_rsrc_dsc_d;
  input reg_dsc_detect;
  input reg_tcfg_gnt;
  input lnk_up_thrtl;
  input out;
  input pipe_userclk1_in;
  input cfg_pm_turnoff_ok_n;
  input pcie_drp_clk;
  input pcie_drp_en;
  input pcie_drp_we;
  input pipe_pclk_in;
  input pipe_rx0_chanisaligned;
  input pipe_rx0_elec_idle;
  input pipe_rx0_phy_status;
  input pipe_rx0_valid;
  input pl_directed_link_auton;
  input pl_directed_link_speed;
  input pl_downstream_deemph_source;
  input pl_transmit_hot_rst;
  input pl_upstream_prefer_deemph;
  input sys_rst_n;
  input rx_np_ok;
  input rx_np_req;
  input trn_tcfg_gnt;
  input [3:0]pcie_block_i_5;
  input trn_teof;
  input trn_tsof;
  input trn_tsrc_rdy;
  input pipe_userclk2_in;
  input [127:0]cfg_err_aer_headerlog;
  input [63:0]trn_td;
  input [15:0]pcie_drp_di;
  input [15:0]pipe_rx0_data;
  input [1:0]cfg_pm_force_state;
  input [1:0]pipe_rx0_char_is_k;
  input [1:0]pl_directed_link_change;
  input [1:0]pl_directed_link_width;
  input [0:0]trn_trem;
  input [2:0]cfg_ds_function_number;
  input [2:0]pipe_rx0_status;
  input [2:0]fc_sel;
  input [31:0]cfg_mgmt_di;
  input [3:0]cfg_mgmt_byte_en_n;
  input [47:0]cfg_err_tlp_cpl_header;
  input [4:0]cfg_aer_interrupt_msgnum;
  input [4:0]cfg_ds_device_number;
  input [4:0]cfg_pciecap_interrupt_msgnum;
  input [63:0]cfg_dsn;
  input [7:0]cfg_ds_bus_number;
  input [7:0]cfg_interrupt_di;
  input [8:0]pcie_drp_addr;
  input [9:0]cfg_mgmt_dwaddr;

  wire [0:0]E;
  wire bridge_reset_int;
  wire cfg_aer_ecrc_check_en;
  wire cfg_aer_ecrc_gen_en;
  wire [4:0]cfg_aer_interrupt_msgnum;
  wire cfg_aer_rooterr_corr_err_received;
  wire cfg_aer_rooterr_corr_err_reporting_en;
  wire cfg_aer_rooterr_fatal_err_received;
  wire cfg_aer_rooterr_fatal_err_reporting_en;
  wire cfg_aer_rooterr_non_fatal_err_received;
  wire cfg_aer_rooterr_non_fatal_err_reporting_en;
  wire cfg_bridge_serr_en;
  wire [4:0]cfg_command;
  wire [14:0]cfg_dcommand;
  wire [11:0]cfg_dcommand2;
  wire [7:0]cfg_ds_bus_number;
  wire [4:0]cfg_ds_device_number;
  wire [2:0]cfg_ds_function_number;
  wire [63:0]cfg_dsn;
  wire [3:0]cfg_dstatus;
  wire [127:0]cfg_err_aer_headerlog;
  wire cfg_err_aer_headerlog_set;
  wire cfg_err_aer_headerlog_set_n;
  wire cfg_err_atomic_egress_blocked;
  wire cfg_err_cor;
  wire cfg_err_cpl_abort;
  wire cfg_err_cpl_rdy;
  wire cfg_err_cpl_rdy_n;
  wire cfg_err_cpl_timeout;
  wire cfg_err_cpl_unexpect;
  wire cfg_err_ecrc;
  wire cfg_err_internal_cor;
  wire cfg_err_internal_uncor;
  wire cfg_err_locked;
  wire cfg_err_malformed;
  wire cfg_err_mc_blocked;
  wire cfg_err_norecovery;
  wire cfg_err_poisoned;
  wire cfg_err_posted;
  wire [47:0]cfg_err_tlp_cpl_header;
  wire cfg_err_ur;
  wire cfg_interrupt;
  wire cfg_interrupt_assert;
  wire [7:0]cfg_interrupt_di;
  wire [7:0]cfg_interrupt_do;
  wire [2:0]cfg_interrupt_mmenable;
  wire cfg_interrupt_msienable;
  wire cfg_interrupt_msixenable;
  wire cfg_interrupt_msixfm;
  wire cfg_interrupt_rdy;
  wire cfg_interrupt_rdy_n;
  wire cfg_interrupt_stat;
  wire [10:0]cfg_lcommand;
  wire [9:0]cfg_lstatus;
  wire [3:0]cfg_mgmt_byte_en_n;
  wire [31:0]cfg_mgmt_di;
  wire [31:0]cfg_mgmt_do;
  wire [9:0]cfg_mgmt_dwaddr;
  wire cfg_mgmt_rd_en;
  wire cfg_mgmt_rd_wr_done;
  wire cfg_mgmt_rd_wr_done_n;
  wire cfg_mgmt_wr_en;
  wire cfg_mgmt_wr_readonly;
  wire cfg_mgmt_wr_rw1c_as_rw;
  wire [15:0]cfg_msg_data;
  wire cfg_msg_received;
  wire cfg_msg_received_assert_int_a;
  wire cfg_msg_received_assert_int_b;
  wire cfg_msg_received_assert_int_c;
  wire cfg_msg_received_assert_int_d;
  wire cfg_msg_received_deassert_int_a;
  wire cfg_msg_received_deassert_int_b;
  wire cfg_msg_received_deassert_int_c;
  wire cfg_msg_received_deassert_int_d;
  wire cfg_msg_received_err_cor;
  wire cfg_msg_received_err_fatal;
  wire cfg_msg_received_err_non_fatal;
  wire cfg_msg_received_pm_as_nak;
  wire cfg_msg_received_pm_pme;
  wire cfg_msg_received_pme_to_ack;
  wire cfg_msg_received_setslotpowerlimit;
  wire [2:0]cfg_pcie_link_state;
  wire [4:0]cfg_pciecap_interrupt_msgnum;
  wire [1:0]cfg_pm_force_state;
  wire cfg_pm_force_state_en;
  wire cfg_pm_halt_aspm_l0s;
  wire cfg_pm_halt_aspm_l1;
  wire cfg_pm_turnoff_ok_n;
  wire cfg_pm_wake;
  wire cfg_pmcsr_pme_en;
  wire cfg_pmcsr_pme_status;
  wire [1:0]cfg_pmcsr_powerstate;
  wire cfg_received_func_lvl_rst;
  wire cfg_received_func_lvl_rst_n;
  wire cfg_root_control_pme_int_en;
  wire cfg_root_control_syserr_corr_err_en;
  wire cfg_root_control_syserr_fatal_err_en;
  wire cfg_root_control_syserr_non_fatal_err_en;
  wire cfg_slot_control_electromech_il_ctl_pulse;
  wire cfg_to_turnoff;
  wire cfg_trn_pending;
  wire [6:0]cfg_vc_tcvc_map;
  wire dsc_detect;
  wire [11:0]fc_cpld;
  wire [7:0]fc_cplh;
  wire [11:0]fc_npd;
  wire [7:0]fc_nph;
  wire [11:0]fc_pd;
  wire [7:0]fc_ph;
  wire [2:0]fc_sel;
  wire lnk_up_thrtl;
  wire [12:0]mim_rx_raddr;
  wire [67:0]mim_rx_rdata;
  wire mim_rx_ren;
  wire [12:0]mim_rx_waddr;
  wire [67:0]mim_rx_wdata;
  wire mim_rx_wen;
  wire [12:0]mim_tx_raddr;
  wire [68:0]mim_tx_rdata;
  wire mim_tx_ren;
  wire [12:0]mim_tx_waddr;
  wire [68:0]mim_tx_wdata;
  wire mim_tx_wen;
  wire out;
  wire pcie_block_i_0;
  wire pcie_block_i_1;
  wire pcie_block_i_2;
  wire [63:0]pcie_block_i_3;
  wire [0:0]pcie_block_i_4;
  wire [3:0]pcie_block_i_5;
  wire pcie_block_i_i_10_n_0;
  wire pcie_block_i_i_11_n_0;
  wire pcie_block_i_i_12_n_0;
  wire pcie_block_i_i_13_n_0;
  wire pcie_block_i_i_14_n_0;
  wire pcie_block_i_i_15_n_0;
  wire pcie_block_i_i_16_n_0;
  wire pcie_block_i_i_17_n_0;
  wire pcie_block_i_i_18_n_0;
  wire pcie_block_i_i_19_n_0;
  wire pcie_block_i_i_1_n_0;
  wire pcie_block_i_i_20_n_0;
  wire pcie_block_i_i_21_n_0;
  wire pcie_block_i_i_22_n_0;
  wire pcie_block_i_i_23_n_0;
  wire pcie_block_i_i_24_n_0;
  wire pcie_block_i_i_25_n_0;
  wire pcie_block_i_i_27_n_0;
  wire pcie_block_i_i_28_n_0;
  wire pcie_block_i_i_2_n_0;
  wire pcie_block_i_i_3_n_0;
  wire pcie_block_i_i_4_n_0;
  wire pcie_block_i_i_5_n_0;
  wire pcie_block_i_i_6_n_0;
  wire pcie_block_i_i_7_n_0;
  wire pcie_block_i_i_8_n_0;
  wire pcie_block_i_i_9_n_0;
  wire pcie_block_i_n_100;
  wire pcie_block_i_n_101;
  wire pcie_block_i_n_102;
  wire pcie_block_i_n_103;
  wire pcie_block_i_n_104;
  wire pcie_block_i_n_105;
  wire pcie_block_i_n_106;
  wire pcie_block_i_n_107;
  wire pcie_block_i_n_108;
  wire pcie_block_i_n_1097;
  wire pcie_block_i_n_1098;
  wire pcie_block_i_n_1099;
  wire pcie_block_i_n_1100;
  wire pcie_block_i_n_1101;
  wire pcie_block_i_n_1102;
  wire pcie_block_i_n_1103;
  wire pcie_block_i_n_1143;
  wire pcie_block_i_n_140;
  wire pcie_block_i_n_141;
  wire pcie_block_i_n_142;
  wire pcie_block_i_n_143;
  wire pcie_block_i_n_144;
  wire pcie_block_i_n_145;
  wire pcie_block_i_n_146;
  wire pcie_block_i_n_155;
  wire pcie_block_i_n_156;
  wire pcie_block_i_n_157;
  wire pcie_block_i_n_158;
  wire pcie_block_i_n_159;
  wire pcie_block_i_n_160;
  wire pcie_block_i_n_169;
  wire pcie_block_i_n_172;
  wire pcie_block_i_n_173;
  wire pcie_block_i_n_174;
  wire pcie_block_i_n_175;
  wire pcie_block_i_n_176;
  wire pcie_block_i_n_177;
  wire pcie_block_i_n_178;
  wire pcie_block_i_n_179;
  wire pcie_block_i_n_180;
  wire pcie_block_i_n_181;
  wire pcie_block_i_n_182;
  wire pcie_block_i_n_183;
  wire pcie_block_i_n_184;
  wire pcie_block_i_n_185;
  wire pcie_block_i_n_186;
  wire pcie_block_i_n_187;
  wire pcie_block_i_n_188;
  wire pcie_block_i_n_189;
  wire pcie_block_i_n_190;
  wire pcie_block_i_n_191;
  wire pcie_block_i_n_192;
  wire pcie_block_i_n_193;
  wire pcie_block_i_n_194;
  wire pcie_block_i_n_195;
  wire pcie_block_i_n_610;
  wire pcie_block_i_n_611;
  wire pcie_block_i_n_618;
  wire pcie_block_i_n_619;
  wire pcie_block_i_n_687;
  wire pcie_block_i_n_688;
  wire pcie_block_i_n_689;
  wire pcie_block_i_n_690;
  wire pcie_block_i_n_691;
  wire pcie_block_i_n_704;
  wire pcie_block_i_n_705;
  wire pcie_block_i_n_706;
  wire pcie_block_i_n_707;
  wire pcie_block_i_n_708;
  wire pcie_block_i_n_709;
  wire pcie_block_i_n_710;
  wire pcie_block_i_n_711;
  wire pcie_block_i_n_712;
  wire pcie_block_i_n_713;
  wire pcie_block_i_n_714;
  wire pcie_block_i_n_715;
  wire pcie_block_i_n_716;
  wire pcie_block_i_n_717;
  wire pcie_block_i_n_718;
  wire pcie_block_i_n_719;
  wire pcie_block_i_n_72;
  wire pcie_block_i_n_720;
  wire pcie_block_i_n_721;
  wire pcie_block_i_n_722;
  wire pcie_block_i_n_723;
  wire pcie_block_i_n_724;
  wire pcie_block_i_n_725;
  wire pcie_block_i_n_726;
  wire pcie_block_i_n_727;
  wire pcie_block_i_n_728;
  wire pcie_block_i_n_729;
  wire pcie_block_i_n_730;
  wire pcie_block_i_n_731;
  wire pcie_block_i_n_732;
  wire pcie_block_i_n_733;
  wire pcie_block_i_n_734;
  wire pcie_block_i_n_735;
  wire pcie_block_i_n_736;
  wire pcie_block_i_n_737;
  wire pcie_block_i_n_738;
  wire pcie_block_i_n_739;
  wire pcie_block_i_n_740;
  wire pcie_block_i_n_741;
  wire pcie_block_i_n_742;
  wire pcie_block_i_n_743;
  wire pcie_block_i_n_744;
  wire pcie_block_i_n_745;
  wire pcie_block_i_n_746;
  wire pcie_block_i_n_747;
  wire pcie_block_i_n_748;
  wire pcie_block_i_n_749;
  wire pcie_block_i_n_75;
  wire pcie_block_i_n_750;
  wire pcie_block_i_n_751;
  wire pcie_block_i_n_752;
  wire pcie_block_i_n_753;
  wire pcie_block_i_n_754;
  wire pcie_block_i_n_755;
  wire pcie_block_i_n_756;
  wire pcie_block_i_n_757;
  wire pcie_block_i_n_758;
  wire pcie_block_i_n_759;
  wire pcie_block_i_n_76;
  wire pcie_block_i_n_760;
  wire pcie_block_i_n_761;
  wire pcie_block_i_n_762;
  wire pcie_block_i_n_763;
  wire pcie_block_i_n_764;
  wire pcie_block_i_n_765;
  wire pcie_block_i_n_766;
  wire pcie_block_i_n_767;
  wire pcie_block_i_n_768;
  wire pcie_block_i_n_769;
  wire pcie_block_i_n_77;
  wire pcie_block_i_n_770;
  wire pcie_block_i_n_771;
  wire pcie_block_i_n_772;
  wire pcie_block_i_n_773;
  wire pcie_block_i_n_774;
  wire pcie_block_i_n_775;
  wire pcie_block_i_n_776;
  wire pcie_block_i_n_777;
  wire pcie_block_i_n_778;
  wire pcie_block_i_n_779;
  wire pcie_block_i_n_78;
  wire pcie_block_i_n_780;
  wire pcie_block_i_n_781;
  wire pcie_block_i_n_782;
  wire pcie_block_i_n_783;
  wire pcie_block_i_n_784;
  wire pcie_block_i_n_785;
  wire pcie_block_i_n_786;
  wire pcie_block_i_n_787;
  wire pcie_block_i_n_788;
  wire pcie_block_i_n_789;
  wire pcie_block_i_n_790;
  wire pcie_block_i_n_791;
  wire pcie_block_i_n_792;
  wire pcie_block_i_n_793;
  wire pcie_block_i_n_794;
  wire pcie_block_i_n_795;
  wire pcie_block_i_n_796;
  wire pcie_block_i_n_797;
  wire pcie_block_i_n_798;
  wire pcie_block_i_n_799;
  wire pcie_block_i_n_800;
  wire pcie_block_i_n_801;
  wire pcie_block_i_n_802;
  wire pcie_block_i_n_803;
  wire pcie_block_i_n_804;
  wire pcie_block_i_n_805;
  wire pcie_block_i_n_806;
  wire pcie_block_i_n_807;
  wire pcie_block_i_n_808;
  wire pcie_block_i_n_809;
  wire pcie_block_i_n_810;
  wire pcie_block_i_n_811;
  wire pcie_block_i_n_812;
  wire pcie_block_i_n_813;
  wire pcie_block_i_n_814;
  wire pcie_block_i_n_815;
  wire pcie_block_i_n_816;
  wire pcie_block_i_n_817;
  wire pcie_block_i_n_818;
  wire pcie_block_i_n_819;
  wire pcie_block_i_n_820;
  wire pcie_block_i_n_821;
  wire pcie_block_i_n_822;
  wire pcie_block_i_n_823;
  wire pcie_block_i_n_824;
  wire pcie_block_i_n_825;
  wire pcie_block_i_n_826;
  wire pcie_block_i_n_827;
  wire pcie_block_i_n_828;
  wire pcie_block_i_n_829;
  wire pcie_block_i_n_830;
  wire pcie_block_i_n_831;
  wire pcie_block_i_n_832;
  wire pcie_block_i_n_833;
  wire pcie_block_i_n_834;
  wire pcie_block_i_n_835;
  wire pcie_block_i_n_836;
  wire pcie_block_i_n_837;
  wire pcie_block_i_n_838;
  wire pcie_block_i_n_839;
  wire pcie_block_i_n_84;
  wire pcie_block_i_n_840;
  wire pcie_block_i_n_841;
  wire pcie_block_i_n_842;
  wire pcie_block_i_n_843;
  wire pcie_block_i_n_844;
  wire pcie_block_i_n_845;
  wire pcie_block_i_n_846;
  wire pcie_block_i_n_847;
  wire pcie_block_i_n_848;
  wire pcie_block_i_n_849;
  wire pcie_block_i_n_85;
  wire pcie_block_i_n_850;
  wire pcie_block_i_n_851;
  wire pcie_block_i_n_852;
  wire pcie_block_i_n_853;
  wire pcie_block_i_n_854;
  wire pcie_block_i_n_855;
  wire pcie_block_i_n_856;
  wire pcie_block_i_n_857;
  wire pcie_block_i_n_858;
  wire pcie_block_i_n_859;
  wire pcie_block_i_n_86;
  wire pcie_block_i_n_860;
  wire pcie_block_i_n_861;
  wire pcie_block_i_n_862;
  wire pcie_block_i_n_863;
  wire pcie_block_i_n_864;
  wire pcie_block_i_n_865;
  wire pcie_block_i_n_866;
  wire pcie_block_i_n_867;
  wire pcie_block_i_n_868;
  wire pcie_block_i_n_869;
  wire pcie_block_i_n_87;
  wire pcie_block_i_n_870;
  wire pcie_block_i_n_871;
  wire pcie_block_i_n_872;
  wire pcie_block_i_n_873;
  wire pcie_block_i_n_874;
  wire pcie_block_i_n_875;
  wire pcie_block_i_n_876;
  wire pcie_block_i_n_877;
  wire pcie_block_i_n_878;
  wire pcie_block_i_n_879;
  wire pcie_block_i_n_88;
  wire pcie_block_i_n_880;
  wire pcie_block_i_n_881;
  wire pcie_block_i_n_882;
  wire pcie_block_i_n_883;
  wire pcie_block_i_n_884;
  wire pcie_block_i_n_885;
  wire pcie_block_i_n_886;
  wire pcie_block_i_n_887;
  wire pcie_block_i_n_888;
  wire pcie_block_i_n_889;
  wire pcie_block_i_n_89;
  wire pcie_block_i_n_890;
  wire pcie_block_i_n_891;
  wire pcie_block_i_n_892;
  wire pcie_block_i_n_893;
  wire pcie_block_i_n_894;
  wire pcie_block_i_n_895;
  wire pcie_block_i_n_896;
  wire pcie_block_i_n_897;
  wire pcie_block_i_n_898;
  wire pcie_block_i_n_899;
  wire pcie_block_i_n_90;
  wire pcie_block_i_n_900;
  wire pcie_block_i_n_901;
  wire pcie_block_i_n_902;
  wire pcie_block_i_n_903;
  wire pcie_block_i_n_904;
  wire pcie_block_i_n_905;
  wire pcie_block_i_n_906;
  wire pcie_block_i_n_907;
  wire pcie_block_i_n_908;
  wire pcie_block_i_n_909;
  wire pcie_block_i_n_91;
  wire pcie_block_i_n_910;
  wire pcie_block_i_n_911;
  wire pcie_block_i_n_912;
  wire pcie_block_i_n_913;
  wire pcie_block_i_n_914;
  wire pcie_block_i_n_915;
  wire pcie_block_i_n_916;
  wire pcie_block_i_n_917;
  wire pcie_block_i_n_918;
  wire pcie_block_i_n_919;
  wire pcie_block_i_n_92;
  wire pcie_block_i_n_920;
  wire pcie_block_i_n_921;
  wire pcie_block_i_n_922;
  wire pcie_block_i_n_923;
  wire pcie_block_i_n_924;
  wire pcie_block_i_n_925;
  wire pcie_block_i_n_926;
  wire pcie_block_i_n_927;
  wire pcie_block_i_n_928;
  wire pcie_block_i_n_929;
  wire pcie_block_i_n_93;
  wire pcie_block_i_n_930;
  wire pcie_block_i_n_931;
  wire pcie_block_i_n_932;
  wire pcie_block_i_n_933;
  wire pcie_block_i_n_934;
  wire pcie_block_i_n_935;
  wire pcie_block_i_n_936;
  wire pcie_block_i_n_937;
  wire pcie_block_i_n_938;
  wire pcie_block_i_n_939;
  wire pcie_block_i_n_94;
  wire pcie_block_i_n_940;
  wire pcie_block_i_n_941;
  wire pcie_block_i_n_942;
  wire pcie_block_i_n_943;
  wire pcie_block_i_n_944;
  wire pcie_block_i_n_945;
  wire pcie_block_i_n_946;
  wire pcie_block_i_n_947;
  wire pcie_block_i_n_948;
  wire pcie_block_i_n_949;
  wire pcie_block_i_n_95;
  wire pcie_block_i_n_950;
  wire pcie_block_i_n_951;
  wire pcie_block_i_n_952;
  wire pcie_block_i_n_953;
  wire pcie_block_i_n_954;
  wire pcie_block_i_n_955;
  wire pcie_block_i_n_956;
  wire pcie_block_i_n_957;
  wire pcie_block_i_n_958;
  wire pcie_block_i_n_959;
  wire pcie_block_i_n_96;
  wire pcie_block_i_n_98;
  wire pcie_block_i_n_99;
  wire [8:0]pcie_drp_addr;
  wire pcie_drp_clk;
  wire [15:0]pcie_drp_di;
  wire [15:0]pcie_drp_do;
  wire pcie_drp_en;
  wire pcie_drp_rdy;
  wire pcie_drp_we;
  wire pipe_pclk_in;
  wire pipe_rx0_chanisaligned;
  wire [1:0]pipe_rx0_char_is_k;
  wire [15:0]pipe_rx0_data;
  wire pipe_rx0_elec_idle;
  wire pipe_rx0_phy_status;
  wire pipe_rx0_polarity;
  wire [2:0]pipe_rx0_status;
  wire pipe_rx0_valid;
  wire pipe_rx1_polarity;
  wire pipe_rx2_polarity;
  wire pipe_rx3_polarity;
  wire pipe_rx4_polarity;
  wire pipe_rx5_polarity;
  wire pipe_rx6_polarity;
  wire pipe_rx7_polarity;
  wire [1:0]pipe_tx0_char_is_k;
  wire pipe_tx0_compliance;
  wire [15:0]pipe_tx0_data;
  wire pipe_tx0_elec_idle;
  wire [1:0]pipe_tx0_powerdown;
  wire [1:0]pipe_tx1_char_is_k;
  wire pipe_tx1_compliance;
  wire [15:0]pipe_tx1_data;
  wire pipe_tx1_elec_idle;
  wire [1:0]pipe_tx1_powerdown;
  wire [1:0]pipe_tx2_char_is_k;
  wire pipe_tx2_compliance;
  wire [15:0]pipe_tx2_data;
  wire pipe_tx2_elec_idle;
  wire [1:0]pipe_tx2_powerdown;
  wire [1:0]pipe_tx3_char_is_k;
  wire pipe_tx3_compliance;
  wire [15:0]pipe_tx3_data;
  wire pipe_tx3_elec_idle;
  wire [1:0]pipe_tx3_powerdown;
  wire [1:0]pipe_tx4_char_is_k;
  wire pipe_tx4_compliance;
  wire [15:0]pipe_tx4_data;
  wire pipe_tx4_elec_idle;
  wire [1:0]pipe_tx4_powerdown;
  wire [1:0]pipe_tx5_char_is_k;
  wire pipe_tx5_compliance;
  wire [15:0]pipe_tx5_data;
  wire pipe_tx5_elec_idle;
  wire [1:0]pipe_tx5_powerdown;
  wire [1:0]pipe_tx6_char_is_k;
  wire pipe_tx6_compliance;
  wire [15:0]pipe_tx6_data;
  wire pipe_tx6_elec_idle;
  wire [1:0]pipe_tx6_powerdown;
  wire [1:0]pipe_tx7_char_is_k;
  wire pipe_tx7_compliance;
  wire [15:0]pipe_tx7_data;
  wire pipe_tx7_elec_idle;
  wire [1:0]pipe_tx7_powerdown;
  wire pipe_tx_deemph;
  wire [2:0]pipe_tx_margin;
  wire pipe_tx_rate;
  wire pipe_tx_rcvr_det;
  wire pipe_userclk1_in;
  wire pipe_userclk2_in;
  wire pl_directed_change_done;
  wire pl_directed_link_auton;
  wire [1:0]pl_directed_link_change;
  wire pl_directed_link_speed;
  wire [1:0]pl_directed_link_width;
  wire pl_downstream_deemph_source;
  wire [2:0]pl_initial_link_width;
  wire [1:0]pl_lane_reversal_mode;
  wire pl_link_gen2_cap;
  wire pl_link_partner_gen2_supported;
  wire pl_link_upcfg_cap;
  wire [5:0]pl_ltssm_state;
  wire pl_phy_lnk_up;
  wire pl_phy_lnk_up_n;
  wire pl_received_hot_rst;
  wire [1:0]pl_rx_pm_state;
  wire pl_sel_lnk_rate;
  wire [1:0]pl_sel_lnk_width;
  wire pl_transmit_hot_rst;
  wire [2:0]pl_tx_pm_state;
  wire pl_upstream_prefer_deemph;
  wire ppm_L1_thrtl;
  wire ppm_L1_trig;
  wire reg_dsc_detect;
  wire reg_tcfg_gnt;
  wire rsrc_rdy_filtered;
  wire rx_np_ok;
  wire rx_np_req;
  wire src_in;
  wire sys_rst_n;
  wire tbuf_av_min_trig;
  wire tcfg_req_trig;
  wire trn_in_packet;
  wire trn_in_packet_reg;
  wire trn_lnk_up;
  wire [6:0]trn_rbar_hit;
  wire [127:64]trn_rd;
  wire trn_rdst_rdy;
  wire trn_recrc_err;
  wire trn_reof;
  wire trn_rerrfwd;
  wire [1:1]trn_rrem;
  wire trn_rsof;
  wire trn_rsrc_dsc;
  wire trn_rsrc_dsc_d;
  wire trn_rsrc_dsc_prev0;
  wire trn_rsrc_rdy;
  wire [5:0]trn_tbuf_av;
  wire trn_tcfg_gnt;
  wire trn_tcfg_req;
  wire [63:0]trn_td;
  wire trn_tdst_rdy;
  wire trn_teof;
  wire [0:0]trn_trem;
  wire trn_tsof;
  wire trn_tsrc_rdy;
  wire tx_err_drop;
  wire user_reset_int_reg;
  wire user_rst_n;
  wire [3:1]NLW_pcie_block_i_TRNTDSTRDY_UNCONNECTED;

  LUT1 #(
    .INIT(2'h1)) 
    \cfg_bus_number_d[7]_i_2 
       (.I0(cfg_msg_received),
        .O(E));
  LUT1 #(
    .INIT(2'h1)) 
    cfg_err_aer_headerlog_set_INST_0
       (.I0(cfg_err_aer_headerlog_set_n),
        .O(cfg_err_aer_headerlog_set));
  LUT1 #(
    .INIT(2'h1)) 
    cfg_err_cpl_rdy_INST_0
       (.I0(cfg_err_cpl_rdy_n),
        .O(cfg_err_cpl_rdy));
  LUT1 #(
    .INIT(2'h1)) 
    cfg_interrupt_rdy_INST_0
       (.I0(cfg_interrupt_rdy_n),
        .O(cfg_interrupt_rdy));
  LUT1 #(
    .INIT(2'h1)) 
    cfg_mgmt_rd_wr_done_INST_0
       (.I0(cfg_mgmt_rd_wr_done_n),
        .O(cfg_mgmt_rd_wr_done));
  LUT1 #(
    .INIT(2'h1)) 
    cfg_received_func_lvl_rst_INST_0
       (.I0(cfg_received_func_lvl_rst_n),
        .O(cfg_received_func_lvl_rst));
  LUT3 #(
    .INIT(8'h4F)) 
    lnk_up_thrtl_i_1
       (.I0(trn_tdst_rdy),
        .I1(lnk_up_thrtl),
        .I2(out),
        .O(pcie_block_i_2));
  LUT6 #(
    .INIT(64'h0000000027000000)) 
    m_axis_rx_tvalid_i_2
       (.I0(trn_reof),
        .I1(trn_rdst_rdy),
        .I2(trn_rsof),
        .I3(trn_rsrc_dsc),
        .I4(trn_in_packet),
        .I5(trn_rsrc_dsc_d),
        .O(dsc_detect));
  (* BOX_TYPE = "PRIMITIVE" *) 
  PCIE_2_1 #(
    .AER_BASE_PTR(12'h000),
    .AER_CAP_ECRC_CHECK_CAPABLE("FALSE"),
    .AER_CAP_ECRC_GEN_CAPABLE("FALSE"),
    .AER_CAP_ID(16'h0001),
    .AER_CAP_MULTIHEADER("FALSE"),
    .AER_CAP_NEXTPTR(12'h000),
    .AER_CAP_ON("FALSE"),
    .AER_CAP_OPTIONAL_ERR_SUPPORT(24'h000000),
    .AER_CAP_PERMIT_ROOTERR_UPDATE("FALSE"),
    .AER_CAP_VERSION(4'h1),
    .ALLOW_X8_GEN2("FALSE"),
    .BAR0(32'hFFFFFC04),
    .BAR1(32'hFFFFFFFF),
    .BAR2(32'h00000000),
    .BAR3(32'h00000000),
    .BAR4(32'h00000000),
    .BAR5(32'h00000000),
    .CAPABILITIES_PTR(8'h40),
    .CARDBUS_CIS_POINTER(32'h00000000),
    .CFG_ECRC_ERR_CPLSTAT(0),
    .CLASS_CODE(24'h020000),
    .CMD_INTX_IMPLEMENTED("TRUE"),
    .CPL_TIMEOUT_DISABLE_SUPPORTED("FALSE"),
    .CPL_TIMEOUT_RANGES_SUPPORTED(4'h2),
    .CRM_MODULE_RSTS(7'h00),
    .DEV_CAP2_ARI_FORWARDING_SUPPORTED("FALSE"),
    .DEV_CAP2_ATOMICOP32_COMPLETER_SUPPORTED("FALSE"),
    .DEV_CAP2_ATOMICOP64_COMPLETER_SUPPORTED("FALSE"),
    .DEV_CAP2_ATOMICOP_ROUTING_SUPPORTED("FALSE"),
    .DEV_CAP2_CAS128_COMPLETER_SUPPORTED("FALSE"),
    .DEV_CAP2_ENDEND_TLP_PREFIX_SUPPORTED("FALSE"),
    .DEV_CAP2_EXTENDED_FMT_FIELD_SUPPORTED("FALSE"),
    .DEV_CAP2_LTR_MECHANISM_SUPPORTED("FALSE"),
    .DEV_CAP2_MAX_ENDEND_TLP_PREFIXES(2'h0),
    .DEV_CAP2_NO_RO_ENABLED_PRPR_PASSING("FALSE"),
    .DEV_CAP2_TPH_COMPLETER_SUPPORTED(2'h0),
    .DEV_CAP_ENABLE_SLOT_PWR_LIMIT_SCALE("TRUE"),
    .DEV_CAP_ENABLE_SLOT_PWR_LIMIT_VALUE("TRUE"),
    .DEV_CAP_ENDPOINT_L0S_LATENCY(0),
    .DEV_CAP_ENDPOINT_L1_LATENCY(7),
    .DEV_CAP_EXT_TAG_SUPPORTED("FALSE"),
    .DEV_CAP_FUNCTION_LEVEL_RESET_CAPABLE("FALSE"),
    .DEV_CAP_MAX_PAYLOAD_SUPPORTED(2),
    .DEV_CAP_PHANTOM_FUNCTIONS_SUPPORT(0),
    .DEV_CAP_ROLE_BASED_ERROR("TRUE"),
    .DEV_CAP_RSVD_14_12(0),
    .DEV_CAP_RSVD_17_16(0),
    .DEV_CAP_RSVD_31_29(0),
    .DEV_CONTROL_AUX_POWER_SUPPORTED("FALSE"),
    .DEV_CONTROL_EXT_TAG_DEFAULT("FALSE"),
    .DISABLE_ASPM_L1_TIMER("FALSE"),
    .DISABLE_BAR_FILTERING("FALSE"),
    .DISABLE_ERR_MSG("FALSE"),
    .DISABLE_ID_CHECK("FALSE"),
    .DISABLE_LANE_REVERSAL("TRUE"),
    .DISABLE_LOCKED_FILTER("FALSE"),
    .DISABLE_PPM_FILTER("FALSE"),
    .DISABLE_RX_POISONED_RESP("FALSE"),
    .DISABLE_RX_TC_FILTER("FALSE"),
    .DISABLE_SCRAMBLING("FALSE"),
    .DNSTREAM_LINK_NUM(8'h00),
    .DSN_BASE_PTR(12'h100),
    .DSN_CAP_ID(16'h0003),
    .DSN_CAP_NEXTPTR(12'h000),
    .DSN_CAP_ON("TRUE"),
    .DSN_CAP_VERSION(4'h1),
    .ENABLE_MSG_ROUTE(11'h000),
    .ENABLE_RX_TD_ECRC_TRIM("FALSE"),
    .ENDEND_TLP_PREFIX_FORWARDING_SUPPORTED("FALSE"),
    .ENTER_RVRY_EI_L0("TRUE"),
    .EXIT_LOOPBACK_ON_EI("TRUE"),
    .EXPANSION_ROM(32'h00000000),
    .EXT_CFG_CAP_PTR(6'h3F),
    .EXT_CFG_XP_CAP_PTR(10'h3FF),
    .HEADER_TYPE(8'h00),
    .INFER_EI(5'h00),
    .INTERRUPT_PIN(8'h01),
    .INTERRUPT_STAT_AUTO("TRUE"),
    .IS_SWITCH("FALSE"),
    .LAST_CONFIG_DWORD(10'h3FF),
    .LINK_CAP_ASPM_OPTIONALITY("FALSE"),
    .LINK_CAP_ASPM_SUPPORT(1),
    .LINK_CAP_CLOCK_POWER_MANAGEMENT("FALSE"),
    .LINK_CAP_DLL_LINK_ACTIVE_REPORTING_CAP("FALSE"),
    .LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN1(7),
    .LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN2(7),
    .LINK_CAP_L0S_EXIT_LATENCY_GEN1(7),
    .LINK_CAP_L0S_EXIT_LATENCY_GEN2(7),
    .LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN1(7),
    .LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN2(7),
    .LINK_CAP_L1_EXIT_LATENCY_GEN1(7),
    .LINK_CAP_L1_EXIT_LATENCY_GEN2(7),
    .LINK_CAP_LINK_BANDWIDTH_NOTIFICATION_CAP("FALSE"),
    .LINK_CAP_MAX_LINK_SPEED(4'h1),
    .LINK_CAP_MAX_LINK_WIDTH(6'h01),
    .LINK_CAP_RSVD_23(0),
    .LINK_CAP_SURPRISE_DOWN_ERROR_CAPABLE("FALSE"),
    .LINK_CONTROL_RCB(0),
    .LINK_CTRL2_DEEMPHASIS("FALSE"),
    .LINK_CTRL2_HW_AUTONOMOUS_SPEED_DISABLE("FALSE"),
    .LINK_CTRL2_TARGET_LINK_SPEED(4'h0),
    .LINK_STATUS_SLOT_CLOCK_CONFIG("TRUE"),
    .LL_ACK_TIMEOUT(15'h0000),
    .LL_ACK_TIMEOUT_EN("FALSE"),
    .LL_ACK_TIMEOUT_FUNC(0),
    .LL_REPLAY_TIMEOUT(15'h0000),
    .LL_REPLAY_TIMEOUT_EN("FALSE"),
    .LL_REPLAY_TIMEOUT_FUNC(1),
    .LTSSM_MAX_LINK_WIDTH(6'h01),
    .MPS_FORCE("FALSE"),
    .MSIX_BASE_PTR(8'h9C),
    .MSIX_CAP_ID(8'h11),
    .MSIX_CAP_NEXTPTR(8'h00),
    .MSIX_CAP_ON("TRUE"),
    .MSIX_CAP_PBA_BIR(0),
    .MSIX_CAP_PBA_OFFSET(29'h00000000),
    .MSIX_CAP_TABLE_BIR(0),
    .MSIX_CAP_TABLE_OFFSET(29'h00000000),
    .MSIX_CAP_TABLE_SIZE(11'h000),
    .MSI_BASE_PTR(8'h48),
    .MSI_CAP_64_BIT_ADDR_CAPABLE("TRUE"),
    .MSI_CAP_ID(8'h05),
    .MSI_CAP_MULTIMSGCAP(0),
    .MSI_CAP_MULTIMSG_EXTENSION(0),
    .MSI_CAP_NEXTPTR(8'h60),
    .MSI_CAP_ON("TRUE"),
    .MSI_CAP_PER_VECTOR_MASKING_CAPABLE("FALSE"),
    .N_FTS_COMCLK_GEN1(255),
    .N_FTS_COMCLK_GEN2(255),
    .N_FTS_GEN1(255),
    .N_FTS_GEN2(255),
    .PCIE_BASE_PTR(8'h60),
    .PCIE_CAP_CAPABILITY_ID(8'h10),
    .PCIE_CAP_CAPABILITY_VERSION(4'h2),
    .PCIE_CAP_DEVICE_PORT_TYPE(4'h0),
    .PCIE_CAP_NEXTPTR(8'h9C),
    .PCIE_CAP_ON("TRUE"),
    .PCIE_CAP_RSVD_15_14(0),
    .PCIE_CAP_SLOT_IMPLEMENTED("FALSE"),
    .PCIE_REVISION(2),
    .PL_AUTO_CONFIG(0),
    .PL_FAST_TRAIN("TRUE"),
    .PM_ASPML0S_TIMEOUT(15'h0000),
    .PM_ASPML0S_TIMEOUT_EN("FALSE"),
    .PM_ASPML0S_TIMEOUT_FUNC(0),
    .PM_ASPM_FASTEXIT("FALSE"),
    .PM_BASE_PTR(8'h40),
    .PM_CAP_AUXCURRENT(0),
    .PM_CAP_D1SUPPORT("FALSE"),
    .PM_CAP_D2SUPPORT("FALSE"),
    .PM_CAP_DSI("FALSE"),
    .PM_CAP_ID(8'h01),
    .PM_CAP_NEXTPTR(8'h48),
    .PM_CAP_ON("TRUE"),
    .PM_CAP_PMESUPPORT(5'h0F),
    .PM_CAP_PME_CLOCK("FALSE"),
    .PM_CAP_RSVD_04(0),
    .PM_CAP_VERSION(3),
    .PM_CSR_B2B3("FALSE"),
    .PM_CSR_BPCCEN("FALSE"),
    .PM_CSR_NOSOFTRST("TRUE"),
    .PM_DATA0(8'h00),
    .PM_DATA1(8'h00),
    .PM_DATA2(8'h00),
    .PM_DATA3(8'h00),
    .PM_DATA4(8'h00),
    .PM_DATA5(8'h00),
    .PM_DATA6(8'h00),
    .PM_DATA7(8'h00),
    .PM_DATA_SCALE0(2'h0),
    .PM_DATA_SCALE1(2'h0),
    .PM_DATA_SCALE2(2'h0),
    .PM_DATA_SCALE3(2'h0),
    .PM_DATA_SCALE4(2'h0),
    .PM_DATA_SCALE5(2'h0),
    .PM_DATA_SCALE6(2'h0),
    .PM_DATA_SCALE7(2'h0),
    .PM_MF("FALSE"),
    .RBAR_BASE_PTR(12'h000),
    .RBAR_CAP_CONTROL_ENCODEDBAR0(5'h00),
    .RBAR_CAP_CONTROL_ENCODEDBAR1(5'h00),
    .RBAR_CAP_CONTROL_ENCODEDBAR2(5'h00),
    .RBAR_CAP_CONTROL_ENCODEDBAR3(5'h00),
    .RBAR_CAP_CONTROL_ENCODEDBAR4(5'h00),
    .RBAR_CAP_CONTROL_ENCODEDBAR5(5'h00),
    .RBAR_CAP_ID(16'h0015),
    .RBAR_CAP_INDEX0(3'h0),
    .RBAR_CAP_INDEX1(3'h0),
    .RBAR_CAP_INDEX2(3'h0),
    .RBAR_CAP_INDEX3(3'h0),
    .RBAR_CAP_INDEX4(3'h0),
    .RBAR_CAP_INDEX5(3'h0),
    .RBAR_CAP_NEXTPTR(12'h000),
    .RBAR_CAP_ON("FALSE"),
    .RBAR_CAP_SUP0(32'h00000001),
    .RBAR_CAP_SUP1(32'h00000001),
    .RBAR_CAP_SUP2(32'h00000001),
    .RBAR_CAP_SUP3(32'h00000001),
    .RBAR_CAP_SUP4(32'h00000001),
    .RBAR_CAP_SUP5(32'h00000001),
    .RBAR_CAP_VERSION(4'h1),
    .RBAR_NUM(3'h0),
    .RECRC_CHK(0),
    .RECRC_CHK_TRIM("FALSE"),
    .ROOT_CAP_CRS_SW_VISIBILITY("FALSE"),
    .RP_AUTO_SPD(2'h1),
    .RP_AUTO_SPD_LOOPCNT(5'h1F),
    .SELECT_DLL_IF("FALSE"),
    .SIM_VERSION("1.0"),
    .SLOT_CAP_ATT_BUTTON_PRESENT("FALSE"),
    .SLOT_CAP_ATT_INDICATOR_PRESENT("FALSE"),
    .SLOT_CAP_ELEC_INTERLOCK_PRESENT("FALSE"),
    .SLOT_CAP_HOTPLUG_CAPABLE("FALSE"),
    .SLOT_CAP_HOTPLUG_SURPRISE("FALSE"),
    .SLOT_CAP_MRL_SENSOR_PRESENT("FALSE"),
    .SLOT_CAP_NO_CMD_COMPLETED_SUPPORT("FALSE"),
    .SLOT_CAP_PHYSICAL_SLOT_NUM(13'h0000),
    .SLOT_CAP_POWER_CONTROLLER_PRESENT("FALSE"),
    .SLOT_CAP_POWER_INDICATOR_PRESENT("FALSE"),
    .SLOT_CAP_SLOT_POWER_LIMIT_SCALE(0),
    .SLOT_CAP_SLOT_POWER_LIMIT_VALUE(8'h00),
    .SPARE_BIT0(0),
    .SPARE_BIT1(0),
    .SPARE_BIT2(0),
    .SPARE_BIT3(0),
    .SPARE_BIT4(0),
    .SPARE_BIT5(0),
    .SPARE_BIT6(0),
    .SPARE_BIT7(0),
    .SPARE_BIT8(0),
    .SPARE_BYTE0(8'h00),
    .SPARE_BYTE1(8'h00),
    .SPARE_BYTE2(8'h00),
    .SPARE_BYTE3(8'h00),
    .SPARE_WORD0(32'h00000000),
    .SPARE_WORD1(32'h00000000),
    .SPARE_WORD2(32'h00000000),
    .SPARE_WORD3(32'h00000000),
    .SSL_MESSAGE_AUTO("FALSE"),
    .TECRC_EP_INV("FALSE"),
    .TL_RBYPASS("FALSE"),
    .TL_RX_RAM_RADDR_LATENCY(0),
    .TL_RX_RAM_RDATA_LATENCY(2),
    .TL_RX_RAM_WRITE_LATENCY(0),
    .TL_TFC_DISABLE("FALSE"),
    .TL_TX_CHECKS_DISABLE("FALSE"),
    .TL_TX_RAM_RADDR_LATENCY(0),
    .TL_TX_RAM_RDATA_LATENCY(2),
    .TL_TX_RAM_WRITE_LATENCY(0),
    .TRN_DW("FALSE"),
    .TRN_NP_FC("TRUE"),
    .UPCONFIG_CAPABLE("TRUE"),
    .UPSTREAM_FACING("TRUE"),
    .UR_ATOMIC("FALSE"),
    .UR_CFG1("TRUE"),
    .UR_INV_REQ("TRUE"),
    .UR_PRS_RESPONSE("TRUE"),
    .USER_CLK2_DIV2("FALSE"),
    .USER_CLK_FREQ(1),
    .USE_RID_PINS("FALSE"),
    .VC0_CPL_INFINITE("TRUE"),
    .VC0_RX_RAM_LIMIT(13'h07FF),
    .VC0_TOTAL_CREDITS_CD(461),
    .VC0_TOTAL_CREDITS_CH(36),
    .VC0_TOTAL_CREDITS_NPD(24),
    .VC0_TOTAL_CREDITS_NPH(12),
    .VC0_TOTAL_CREDITS_PD(437),
    .VC0_TOTAL_CREDITS_PH(32),
    .VC0_TX_LASTPACKET(29),
    .VC_BASE_PTR(12'h000),
    .VC_CAP_ID(16'h0002),
    .VC_CAP_NEXTPTR(12'h000),
    .VC_CAP_ON("FALSE"),
    .VC_CAP_REJECT_SNOOP_TRANSACTIONS("FALSE"),
    .VC_CAP_VERSION(4'h1),
    .VSEC_BASE_PTR(12'h000),
    .VSEC_CAP_HDR_ID(16'h1234),
    .VSEC_CAP_HDR_LENGTH(12'h018),
    .VSEC_CAP_HDR_REVISION(4'h1),
    .VSEC_CAP_ID(16'h000B),
    .VSEC_CAP_IS_LINK_VISIBLE("TRUE"),
    .VSEC_CAP_NEXTPTR(12'h000),
    .VSEC_CAP_ON("FALSE"),
    .VSEC_CAP_VERSION(4'h1)) 
    pcie_block_i
       (.CFGAERECRCCHECKEN(cfg_aer_ecrc_check_en),
        .CFGAERECRCGENEN(cfg_aer_ecrc_gen_en),
        .CFGAERINTERRUPTMSGNUM(cfg_aer_interrupt_msgnum),
        .CFGAERROOTERRCORRERRRECEIVED(cfg_aer_rooterr_corr_err_received),
        .CFGAERROOTERRCORRERRREPORTINGEN(cfg_aer_rooterr_corr_err_reporting_en),
        .CFGAERROOTERRFATALERRRECEIVED(cfg_aer_rooterr_fatal_err_received),
        .CFGAERROOTERRFATALERRREPORTINGEN(cfg_aer_rooterr_fatal_err_reporting_en),
        .CFGAERROOTERRNONFATALERRRECEIVED(cfg_aer_rooterr_non_fatal_err_received),
        .CFGAERROOTERRNONFATALERRREPORTINGEN(cfg_aer_rooterr_non_fatal_err_reporting_en),
        .CFGBRIDGESERREN(cfg_bridge_serr_en),
        .CFGCOMMANDBUSMASTERENABLE(cfg_command[2]),
        .CFGCOMMANDINTERRUPTDISABLE(cfg_command[4]),
        .CFGCOMMANDIOENABLE(cfg_command[0]),
        .CFGCOMMANDMEMENABLE(cfg_command[1]),
        .CFGCOMMANDSERREN(cfg_command[3]),
        .CFGDEVCONTROL2ARIFORWARDEN(cfg_dcommand2[5]),
        .CFGDEVCONTROL2ATOMICEGRESSBLOCK(cfg_dcommand2[7]),
        .CFGDEVCONTROL2ATOMICREQUESTEREN(cfg_dcommand2[6]),
        .CFGDEVCONTROL2CPLTIMEOUTDIS(cfg_dcommand2[4]),
        .CFGDEVCONTROL2CPLTIMEOUTVAL(cfg_dcommand2[3:0]),
        .CFGDEVCONTROL2IDOCPLEN(cfg_dcommand2[9]),
        .CFGDEVCONTROL2IDOREQEN(cfg_dcommand2[8]),
        .CFGDEVCONTROL2LTREN(cfg_dcommand2[10]),
        .CFGDEVCONTROL2TLPPREFIXBLOCK(cfg_dcommand2[11]),
        .CFGDEVCONTROLAUXPOWEREN(cfg_dcommand[10]),
        .CFGDEVCONTROLCORRERRREPORTINGEN(cfg_dcommand[0]),
        .CFGDEVCONTROLENABLERO(cfg_dcommand[4]),
        .CFGDEVCONTROLEXTTAGEN(cfg_dcommand[8]),
        .CFGDEVCONTROLFATALERRREPORTINGEN(cfg_dcommand[2]),
        .CFGDEVCONTROLMAXPAYLOAD(cfg_dcommand[7:5]),
        .CFGDEVCONTROLMAXREADREQ(cfg_dcommand[14:12]),
        .CFGDEVCONTROLNONFATALREPORTINGEN(cfg_dcommand[1]),
        .CFGDEVCONTROLNOSNOOPEN(cfg_dcommand[11]),
        .CFGDEVCONTROLPHANTOMEN(cfg_dcommand[9]),
        .CFGDEVCONTROLURERRREPORTINGEN(cfg_dcommand[3]),
        .CFGDEVID({1'b1,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b0,1'b1,1'b0,1'b0,1'b1,1'b0,1'b1}),
        .CFGDEVSTATUSCORRERRDETECTED(cfg_dstatus[0]),
        .CFGDEVSTATUSFATALERRDETECTED(cfg_dstatus[2]),
        .CFGDEVSTATUSNONFATALERRDETECTED(cfg_dstatus[1]),
        .CFGDEVSTATUSURDETECTED(cfg_dstatus[3]),
        .CFGDSBUSNUMBER(cfg_ds_bus_number),
        .CFGDSDEVICENUMBER(cfg_ds_device_number),
        .CFGDSFUNCTIONNUMBER(cfg_ds_function_number),
        .CFGDSN(cfg_dsn),
        .CFGERRACSN(1'b1),
        .CFGERRAERHEADERLOG(cfg_err_aer_headerlog),
        .CFGERRAERHEADERLOGSETN(cfg_err_aer_headerlog_set_n),
        .CFGERRATOMICEGRESSBLOCKEDN(pcie_block_i_i_1_n_0),
        .CFGERRCORN(pcie_block_i_i_2_n_0),
        .CFGERRCPLABORTN(pcie_block_i_i_3_n_0),
        .CFGERRCPLRDYN(cfg_err_cpl_rdy_n),
        .CFGERRCPLTIMEOUTN(pcie_block_i_i_4_n_0),
        .CFGERRCPLUNEXPECTN(pcie_block_i_i_5_n_0),
        .CFGERRECRCN(pcie_block_i_i_6_n_0),
        .CFGERRINTERNALCORN(pcie_block_i_i_7_n_0),
        .CFGERRINTERNALUNCORN(pcie_block_i_i_8_n_0),
        .CFGERRLOCKEDN(pcie_block_i_i_9_n_0),
        .CFGERRMALFORMEDN(pcie_block_i_i_10_n_0),
        .CFGERRMCBLOCKEDN(pcie_block_i_i_11_n_0),
        .CFGERRNORECOVERYN(pcie_block_i_i_12_n_0),
        .CFGERRPOISONEDN(pcie_block_i_i_13_n_0),
        .CFGERRPOSTEDN(pcie_block_i_i_14_n_0),
        .CFGERRTLPCPLHEADER(cfg_err_tlp_cpl_header),
        .CFGERRURN(pcie_block_i_i_15_n_0),
        .CFGFORCECOMMONCLOCKOFF(1'b0),
        .CFGFORCEEXTENDEDSYNCON(1'b0),
        .CFGFORCEMPS({1'b0,1'b0,1'b0}),
        .CFGINTERRUPTASSERTN(pcie_block_i_i_16_n_0),
        .CFGINTERRUPTDI(cfg_interrupt_di),
        .CFGINTERRUPTDO(cfg_interrupt_do),
        .CFGINTERRUPTMMENABLE(cfg_interrupt_mmenable),
        .CFGINTERRUPTMSIENABLE(cfg_interrupt_msienable),
        .CFGINTERRUPTMSIXENABLE(cfg_interrupt_msixenable),
        .CFGINTERRUPTMSIXFM(cfg_interrupt_msixfm),
        .CFGINTERRUPTN(pcie_block_i_i_17_n_0),
        .CFGINTERRUPTRDYN(cfg_interrupt_rdy_n),
        .CFGINTERRUPTSTATN(pcie_block_i_i_18_n_0),
        .CFGLINKCONTROLASPMCONTROL(cfg_lcommand[1:0]),
        .CFGLINKCONTROLAUTOBANDWIDTHINTEN(cfg_lcommand[10]),
        .CFGLINKCONTROLBANDWIDTHINTEN(cfg_lcommand[9]),
        .CFGLINKCONTROLCLOCKPMEN(cfg_lcommand[7]),
        .CFGLINKCONTROLCOMMONCLOCK(cfg_lcommand[5]),
        .CFGLINKCONTROLEXTENDEDSYNC(cfg_lcommand[6]),
        .CFGLINKCONTROLHWAUTOWIDTHDIS(cfg_lcommand[8]),
        .CFGLINKCONTROLLINKDISABLE(cfg_lcommand[3]),
        .CFGLINKCONTROLRCB(cfg_lcommand[2]),
        .CFGLINKCONTROLRETRAINLINK(cfg_lcommand[4]),
        .CFGLINKSTATUSAUTOBANDWIDTHSTATUS(cfg_lstatus[9]),
        .CFGLINKSTATUSBANDWIDTHSTATUS(cfg_lstatus[8]),
        .CFGLINKSTATUSCURRENTSPEED(cfg_lstatus[1:0]),
        .CFGLINKSTATUSDLLACTIVE(cfg_lstatus[7]),
        .CFGLINKSTATUSLINKTRAINING(cfg_lstatus[6]),
        .CFGLINKSTATUSNEGOTIATEDWIDTH(cfg_lstatus[5:2]),
        .CFGMGMTBYTEENN(cfg_mgmt_byte_en_n),
        .CFGMGMTDI(cfg_mgmt_di),
        .CFGMGMTDO(cfg_mgmt_do),
        .CFGMGMTDWADDR(cfg_mgmt_dwaddr),
        .CFGMGMTRDENN(pcie_block_i_i_19_n_0),
        .CFGMGMTRDWRDONEN(cfg_mgmt_rd_wr_done_n),
        .CFGMGMTWRENN(pcie_block_i_i_20_n_0),
        .CFGMGMTWRREADONLYN(pcie_block_i_i_21_n_0),
        .CFGMGMTWRRW1CASRWN(pcie_block_i_i_22_n_0),
        .CFGMSGDATA(cfg_msg_data),
        .CFGMSGRECEIVED(cfg_msg_received),
        .CFGMSGRECEIVEDASSERTINTA(cfg_msg_received_assert_int_a),
        .CFGMSGRECEIVEDASSERTINTB(cfg_msg_received_assert_int_b),
        .CFGMSGRECEIVEDASSERTINTC(cfg_msg_received_assert_int_c),
        .CFGMSGRECEIVEDASSERTINTD(cfg_msg_received_assert_int_d),
        .CFGMSGRECEIVEDDEASSERTINTA(cfg_msg_received_deassert_int_a),
        .CFGMSGRECEIVEDDEASSERTINTB(cfg_msg_received_deassert_int_b),
        .CFGMSGRECEIVEDDEASSERTINTC(cfg_msg_received_deassert_int_c),
        .CFGMSGRECEIVEDDEASSERTINTD(cfg_msg_received_deassert_int_d),
        .CFGMSGRECEIVEDERRCOR(cfg_msg_received_err_cor),
        .CFGMSGRECEIVEDERRFATAL(cfg_msg_received_err_fatal),
        .CFGMSGRECEIVEDERRNONFATAL(cfg_msg_received_err_non_fatal),
        .CFGMSGRECEIVEDPMASNAK(cfg_msg_received_pm_as_nak),
        .CFGMSGRECEIVEDPMETO(cfg_to_turnoff),
        .CFGMSGRECEIVEDPMETOACK(cfg_msg_received_pme_to_ack),
        .CFGMSGRECEIVEDPMPME(cfg_msg_received_pm_pme),
        .CFGMSGRECEIVEDSETSLOTPOWERLIMIT(cfg_msg_received_setslotpowerlimit),
        .CFGMSGRECEIVEDUNLOCK(pcie_block_i_n_72),
        .CFGPCIECAPINTERRUPTMSGNUM(cfg_pciecap_interrupt_msgnum),
        .CFGPCIELINKSTATE(cfg_pcie_link_state),
        .CFGPMCSRPMEEN(cfg_pmcsr_pme_en),
        .CFGPMCSRPMESTATUS(cfg_pmcsr_pme_status),
        .CFGPMCSRPOWERSTATE(cfg_pmcsr_powerstate),
        .CFGPMFORCESTATE(cfg_pm_force_state),
        .CFGPMFORCESTATEENN(pcie_block_i_i_23_n_0),
        .CFGPMHALTASPML0SN(pcie_block_i_i_24_n_0),
        .CFGPMHALTASPML1N(pcie_block_i_i_25_n_0),
        .CFGPMRCVASREQL1N(pcie_block_i_n_75),
        .CFGPMRCVENTERL1N(pcie_block_i_n_76),
        .CFGPMRCVENTERL23N(pcie_block_i_n_77),
        .CFGPMRCVREQACKN(pcie_block_i_n_78),
        .CFGPMSENDPMETON(1'b1),
        .CFGPMTURNOFFOKN(cfg_pm_turnoff_ok_n),
        .CFGPMWAKEN(pcie_block_i_i_27_n_0),
        .CFGPORTNUMBER({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .CFGREVID({1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b0,1'b0}),
        .CFGROOTCONTROLPMEINTEN(cfg_root_control_pme_int_en),
        .CFGROOTCONTROLSYSERRCORRERREN(cfg_root_control_syserr_corr_err_en),
        .CFGROOTCONTROLSYSERRFATALERREN(cfg_root_control_syserr_fatal_err_en),
        .CFGROOTCONTROLSYSERRNONFATALERREN(cfg_root_control_syserr_non_fatal_err_en),
        .CFGSLOTCONTROLELECTROMECHILCTLPULSE(cfg_slot_control_electromech_il_ctl_pulse),
        .CFGSUBSYSID({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1}),
        .CFGSUBSYSVENDID({1'b0,1'b1,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b0,1'b0,1'b1,1'b1,1'b0,1'b0,1'b1,1'b0}),
        .CFGTRANSACTION(pcie_block_i_n_84),
        .CFGTRANSACTIONADDR({pcie_block_i_n_1097,pcie_block_i_n_1098,pcie_block_i_n_1099,pcie_block_i_n_1100,pcie_block_i_n_1101,pcie_block_i_n_1102,pcie_block_i_n_1103}),
        .CFGTRANSACTIONTYPE(pcie_block_i_n_85),
        .CFGTRNPENDINGN(pcie_block_i_i_28_n_0),
        .CFGVCTCVCMAP(cfg_vc_tcvc_map),
        .CFGVENDID({1'b0,1'b0,1'b0,1'b1,1'b0,1'b0,1'b0,1'b0,1'b1,1'b1,1'b1,1'b0,1'b1,1'b1,1'b0,1'b0}),
        .CMRSTN(1'b1),
        .CMSTICKYRSTN(1'b1),
        .DBGMODE({1'b0,1'b0}),
        .DBGSCLRA(pcie_block_i_n_86),
        .DBGSCLRB(pcie_block_i_n_87),
        .DBGSCLRC(pcie_block_i_n_88),
        .DBGSCLRD(pcie_block_i_n_89),
        .DBGSCLRE(pcie_block_i_n_90),
        .DBGSCLRF(pcie_block_i_n_91),
        .DBGSCLRG(pcie_block_i_n_92),
        .DBGSCLRH(pcie_block_i_n_93),
        .DBGSCLRI(pcie_block_i_n_94),
        .DBGSCLRJ(pcie_block_i_n_95),
        .DBGSCLRK(pcie_block_i_n_96),
        .DBGSUBMODE(1'b0),
        .DBGVECA({pcie_block_i_n_704,pcie_block_i_n_705,pcie_block_i_n_706,pcie_block_i_n_707,pcie_block_i_n_708,pcie_block_i_n_709,pcie_block_i_n_710,pcie_block_i_n_711,pcie_block_i_n_712,pcie_block_i_n_713,pcie_block_i_n_714,pcie_block_i_n_715,pcie_block_i_n_716,pcie_block_i_n_717,pcie_block_i_n_718,pcie_block_i_n_719,pcie_block_i_n_720,pcie_block_i_n_721,pcie_block_i_n_722,pcie_block_i_n_723,pcie_block_i_n_724,pcie_block_i_n_725,pcie_block_i_n_726,pcie_block_i_n_727,pcie_block_i_n_728,pcie_block_i_n_729,pcie_block_i_n_730,pcie_block_i_n_731,pcie_block_i_n_732,pcie_block_i_n_733,pcie_block_i_n_734,pcie_block_i_n_735,pcie_block_i_n_736,pcie_block_i_n_737,pcie_block_i_n_738,pcie_block_i_n_739,pcie_block_i_n_740,pcie_block_i_n_741,pcie_block_i_n_742,pcie_block_i_n_743,pcie_block_i_n_744,pcie_block_i_n_745,pcie_block_i_n_746,pcie_block_i_n_747,pcie_block_i_n_748,pcie_block_i_n_749,pcie_block_i_n_750,pcie_block_i_n_751,pcie_block_i_n_752,pcie_block_i_n_753,pcie_block_i_n_754,pcie_block_i_n_755,pcie_block_i_n_756,pcie_block_i_n_757,pcie_block_i_n_758,pcie_block_i_n_759,pcie_block_i_n_760,pcie_block_i_n_761,pcie_block_i_n_762,pcie_block_i_n_763,pcie_block_i_n_764,pcie_block_i_n_765,pcie_block_i_n_766,pcie_block_i_n_767}),
        .DBGVECB({pcie_block_i_n_768,pcie_block_i_n_769,pcie_block_i_n_770,pcie_block_i_n_771,pcie_block_i_n_772,pcie_block_i_n_773,pcie_block_i_n_774,pcie_block_i_n_775,pcie_block_i_n_776,pcie_block_i_n_777,pcie_block_i_n_778,pcie_block_i_n_779,pcie_block_i_n_780,pcie_block_i_n_781,pcie_block_i_n_782,pcie_block_i_n_783,pcie_block_i_n_784,pcie_block_i_n_785,pcie_block_i_n_786,pcie_block_i_n_787,pcie_block_i_n_788,pcie_block_i_n_789,pcie_block_i_n_790,pcie_block_i_n_791,pcie_block_i_n_792,pcie_block_i_n_793,pcie_block_i_n_794,pcie_block_i_n_795,pcie_block_i_n_796,pcie_block_i_n_797,pcie_block_i_n_798,pcie_block_i_n_799,pcie_block_i_n_800,pcie_block_i_n_801,pcie_block_i_n_802,pcie_block_i_n_803,pcie_block_i_n_804,pcie_block_i_n_805,pcie_block_i_n_806,pcie_block_i_n_807,pcie_block_i_n_808,pcie_block_i_n_809,pcie_block_i_n_810,pcie_block_i_n_811,pcie_block_i_n_812,pcie_block_i_n_813,pcie_block_i_n_814,pcie_block_i_n_815,pcie_block_i_n_816,pcie_block_i_n_817,pcie_block_i_n_818,pcie_block_i_n_819,pcie_block_i_n_820,pcie_block_i_n_821,pcie_block_i_n_822,pcie_block_i_n_823,pcie_block_i_n_824,pcie_block_i_n_825,pcie_block_i_n_826,pcie_block_i_n_827,pcie_block_i_n_828,pcie_block_i_n_829,pcie_block_i_n_830,pcie_block_i_n_831}),
        .DBGVECC({pcie_block_i_n_172,pcie_block_i_n_173,pcie_block_i_n_174,pcie_block_i_n_175,pcie_block_i_n_176,pcie_block_i_n_177,pcie_block_i_n_178,pcie_block_i_n_179,pcie_block_i_n_180,pcie_block_i_n_181,pcie_block_i_n_182,pcie_block_i_n_183}),
        .DLRSTN(1'b1),
        .DRPADDR(pcie_drp_addr),
        .DRPCLK(pcie_drp_clk),
        .DRPDI(pcie_drp_di),
        .DRPDO(pcie_drp_do),
        .DRPEN(pcie_drp_en),
        .DRPRDY(pcie_drp_rdy),
        .DRPWE(pcie_drp_we),
        .FUNCLVLRSTN(1'b1),
        .LL2BADDLLPERR(pcie_block_i_n_98),
        .LL2BADTLPERR(pcie_block_i_n_99),
        .LL2LINKSTATUS({pcie_block_i_n_687,pcie_block_i_n_688,pcie_block_i_n_689,pcie_block_i_n_690,pcie_block_i_n_691}),
        .LL2PROTOCOLERR(pcie_block_i_n_100),
        .LL2RECEIVERERR(pcie_block_i_n_101),
        .LL2REPLAYROERR(pcie_block_i_n_102),
        .LL2REPLAYTOERR(pcie_block_i_n_103),
        .LL2SENDASREQL1(1'b0),
        .LL2SENDENTERL1(1'b0),
        .LL2SENDENTERL23(1'b0),
        .LL2SENDPMACK(1'b0),
        .LL2SUSPENDNOW(1'b0),
        .LL2SUSPENDOK(pcie_block_i_n_104),
        .LL2TFCINIT1SEQ(pcie_block_i_n_105),
        .LL2TFCINIT2SEQ(pcie_block_i_n_106),
        .LL2TLPRCV(1'b0),
        .LL2TXIDLE(pcie_block_i_n_107),
        .LNKCLKEN(pcie_block_i_n_108),
        .MIMRXRADDR(mim_rx_raddr),
        .MIMRXRDATA(mim_rx_rdata),
        .MIMRXREN(mim_rx_ren),
        .MIMRXWADDR(mim_rx_waddr),
        .MIMRXWDATA(mim_rx_wdata),
        .MIMRXWEN(mim_rx_wen),
        .MIMTXRADDR(mim_tx_raddr),
        .MIMTXRDATA(mim_tx_rdata),
        .MIMTXREN(mim_tx_ren),
        .MIMTXWADDR(mim_tx_waddr),
        .MIMTXWDATA(mim_tx_wdata),
        .MIMTXWEN(mim_tx_wen),
        .PIPECLK(pipe_pclk_in),
        .PIPERX0CHANISALIGNED(pipe_rx0_chanisaligned),
        .PIPERX0CHARISK(pipe_rx0_char_is_k),
        .PIPERX0DATA(pipe_rx0_data),
        .PIPERX0ELECIDLE(pipe_rx0_elec_idle),
        .PIPERX0PHYSTATUS(pipe_rx0_phy_status),
        .PIPERX0POLARITY(pipe_rx0_polarity),
        .PIPERX0STATUS(pipe_rx0_status),
        .PIPERX0VALID(pipe_rx0_valid),
        .PIPERX1CHANISALIGNED(1'b0),
        .PIPERX1CHARISK({1'b0,1'b0}),
        .PIPERX1DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX1ELECIDLE(1'b1),
        .PIPERX1PHYSTATUS(1'b0),
        .PIPERX1POLARITY(pipe_rx1_polarity),
        .PIPERX1STATUS({1'b0,1'b0,1'b0}),
        .PIPERX1VALID(1'b0),
        .PIPERX2CHANISALIGNED(1'b0),
        .PIPERX2CHARISK({1'b0,1'b0}),
        .PIPERX2DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX2ELECIDLE(1'b1),
        .PIPERX2PHYSTATUS(1'b0),
        .PIPERX2POLARITY(pipe_rx2_polarity),
        .PIPERX2STATUS({1'b0,1'b0,1'b0}),
        .PIPERX2VALID(1'b0),
        .PIPERX3CHANISALIGNED(1'b0),
        .PIPERX3CHARISK({1'b0,1'b0}),
        .PIPERX3DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX3ELECIDLE(1'b1),
        .PIPERX3PHYSTATUS(1'b0),
        .PIPERX3POLARITY(pipe_rx3_polarity),
        .PIPERX3STATUS({1'b0,1'b0,1'b0}),
        .PIPERX3VALID(1'b0),
        .PIPERX4CHANISALIGNED(1'b0),
        .PIPERX4CHARISK({1'b0,1'b0}),
        .PIPERX4DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX4ELECIDLE(1'b1),
        .PIPERX4PHYSTATUS(1'b0),
        .PIPERX4POLARITY(pipe_rx4_polarity),
        .PIPERX4STATUS({1'b0,1'b0,1'b0}),
        .PIPERX4VALID(1'b0),
        .PIPERX5CHANISALIGNED(1'b0),
        .PIPERX5CHARISK({1'b0,1'b0}),
        .PIPERX5DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX5ELECIDLE(1'b1),
        .PIPERX5PHYSTATUS(1'b0),
        .PIPERX5POLARITY(pipe_rx5_polarity),
        .PIPERX5STATUS({1'b0,1'b0,1'b0}),
        .PIPERX5VALID(1'b0),
        .PIPERX6CHANISALIGNED(1'b0),
        .PIPERX6CHARISK({1'b0,1'b0}),
        .PIPERX6DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX6ELECIDLE(1'b1),
        .PIPERX6PHYSTATUS(1'b0),
        .PIPERX6POLARITY(pipe_rx6_polarity),
        .PIPERX6STATUS({1'b0,1'b0,1'b0}),
        .PIPERX6VALID(1'b0),
        .PIPERX7CHANISALIGNED(1'b0),
        .PIPERX7CHARISK({1'b0,1'b0}),
        .PIPERX7DATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PIPERX7ELECIDLE(1'b1),
        .PIPERX7PHYSTATUS(1'b0),
        .PIPERX7POLARITY(pipe_rx7_polarity),
        .PIPERX7STATUS({1'b0,1'b0,1'b0}),
        .PIPERX7VALID(1'b0),
        .PIPETX0CHARISK(pipe_tx0_char_is_k),
        .PIPETX0COMPLIANCE(pipe_tx0_compliance),
        .PIPETX0DATA(pipe_tx0_data),
        .PIPETX0ELECIDLE(pipe_tx0_elec_idle),
        .PIPETX0POWERDOWN(pipe_tx0_powerdown),
        .PIPETX1CHARISK(pipe_tx1_char_is_k),
        .PIPETX1COMPLIANCE(pipe_tx1_compliance),
        .PIPETX1DATA(pipe_tx1_data),
        .PIPETX1ELECIDLE(pipe_tx1_elec_idle),
        .PIPETX1POWERDOWN(pipe_tx1_powerdown),
        .PIPETX2CHARISK(pipe_tx2_char_is_k),
        .PIPETX2COMPLIANCE(pipe_tx2_compliance),
        .PIPETX2DATA(pipe_tx2_data),
        .PIPETX2ELECIDLE(pipe_tx2_elec_idle),
        .PIPETX2POWERDOWN(pipe_tx2_powerdown),
        .PIPETX3CHARISK(pipe_tx3_char_is_k),
        .PIPETX3COMPLIANCE(pipe_tx3_compliance),
        .PIPETX3DATA(pipe_tx3_data),
        .PIPETX3ELECIDLE(pipe_tx3_elec_idle),
        .PIPETX3POWERDOWN(pipe_tx3_powerdown),
        .PIPETX4CHARISK(pipe_tx4_char_is_k),
        .PIPETX4COMPLIANCE(pipe_tx4_compliance),
        .PIPETX4DATA(pipe_tx4_data),
        .PIPETX4ELECIDLE(pipe_tx4_elec_idle),
        .PIPETX4POWERDOWN(pipe_tx4_powerdown),
        .PIPETX5CHARISK(pipe_tx5_char_is_k),
        .PIPETX5COMPLIANCE(pipe_tx5_compliance),
        .PIPETX5DATA(pipe_tx5_data),
        .PIPETX5ELECIDLE(pipe_tx5_elec_idle),
        .PIPETX5POWERDOWN(pipe_tx5_powerdown),
        .PIPETX6CHARISK(pipe_tx6_char_is_k),
        .PIPETX6COMPLIANCE(pipe_tx6_compliance),
        .PIPETX6DATA(pipe_tx6_data),
        .PIPETX6ELECIDLE(pipe_tx6_elec_idle),
        .PIPETX6POWERDOWN(pipe_tx6_powerdown),
        .PIPETX7CHARISK(pipe_tx7_char_is_k),
        .PIPETX7COMPLIANCE(pipe_tx7_compliance),
        .PIPETX7DATA(pipe_tx7_data),
        .PIPETX7ELECIDLE(pipe_tx7_elec_idle),
        .PIPETX7POWERDOWN(pipe_tx7_powerdown),
        .PIPETXDEEMPH(pipe_tx_deemph),
        .PIPETXMARGIN(pipe_tx_margin),
        .PIPETXRATE(pipe_tx_rate),
        .PIPETXRCVRDET(pipe_tx_rcvr_det),
        .PIPETXRESET(pcie_block_i_n_140),
        .PL2DIRECTEDLSTATE({1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PL2L0REQ(pcie_block_i_n_141),
        .PL2LINKUP(pcie_block_i_n_142),
        .PL2RECEIVERERR(pcie_block_i_n_143),
        .PL2RECOVERY(pcie_block_i_n_144),
        .PL2RXELECIDLE(pcie_block_i_n_145),
        .PL2RXPMSTATE({pcie_block_i_n_610,pcie_block_i_n_611}),
        .PL2SUSPENDOK(pcie_block_i_n_146),
        .PLDBGMODE({1'b0,1'b0,1'b0}),
        .PLDBGVEC({pcie_block_i_n_184,pcie_block_i_n_185,pcie_block_i_n_186,pcie_block_i_n_187,pcie_block_i_n_188,pcie_block_i_n_189,pcie_block_i_n_190,pcie_block_i_n_191,pcie_block_i_n_192,pcie_block_i_n_193,pcie_block_i_n_194,pcie_block_i_n_195}),
        .PLDIRECTEDCHANGEDONE(pl_directed_change_done),
        .PLDIRECTEDLINKAUTON(pl_directed_link_auton),
        .PLDIRECTEDLINKCHANGE(pl_directed_link_change),
        .PLDIRECTEDLINKSPEED(pl_directed_link_speed),
        .PLDIRECTEDLINKWIDTH(pl_directed_link_width),
        .PLDIRECTEDLTSSMNEW({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PLDIRECTEDLTSSMNEWVLD(1'b0),
        .PLDIRECTEDLTSSMSTALL(1'b0),
        .PLDOWNSTREAMDEEMPHSOURCE(pl_downstream_deemph_source),
        .PLINITIALLINKWIDTH(pl_initial_link_width),
        .PLLANEREVERSALMODE(pl_lane_reversal_mode),
        .PLLINKGEN2CAP(pl_link_gen2_cap),
        .PLLINKPARTNERGEN2SUPPORTED(pl_link_partner_gen2_supported),
        .PLLINKUPCFGCAP(pl_link_upcfg_cap),
        .PLLTSSMSTATE(pl_ltssm_state),
        .PLPHYLNKUPN(pl_phy_lnk_up_n),
        .PLRECEIVEDHOTRST(pl_received_hot_rst),
        .PLRSTN(1'b1),
        .PLRXPMSTATE(pl_rx_pm_state),
        .PLSELLNKRATE(pl_sel_lnk_rate),
        .PLSELLNKWIDTH(pl_sel_lnk_width),
        .PLTRANSMITHOTRST(pl_transmit_hot_rst),
        .PLTXPMSTATE(pl_tx_pm_state),
        .PLUPSTREAMPREFERDEEMPH(pl_upstream_prefer_deemph),
        .RECEIVEDFUNCLVLRSTN(cfg_received_func_lvl_rst_n),
        .SYSRSTN(sys_rst_n),
        .TL2ASPMSUSPENDCREDITCHECK(1'b0),
        .TL2ASPMSUSPENDCREDITCHECKOK(pcie_block_i_n_155),
        .TL2ASPMSUSPENDREQ(pcie_block_i_n_156),
        .TL2ERRFCPE(pcie_block_i_n_157),
        .TL2ERRHDR({pcie_block_i_n_832,pcie_block_i_n_833,pcie_block_i_n_834,pcie_block_i_n_835,pcie_block_i_n_836,pcie_block_i_n_837,pcie_block_i_n_838,pcie_block_i_n_839,pcie_block_i_n_840,pcie_block_i_n_841,pcie_block_i_n_842,pcie_block_i_n_843,pcie_block_i_n_844,pcie_block_i_n_845,pcie_block_i_n_846,pcie_block_i_n_847,pcie_block_i_n_848,pcie_block_i_n_849,pcie_block_i_n_850,pcie_block_i_n_851,pcie_block_i_n_852,pcie_block_i_n_853,pcie_block_i_n_854,pcie_block_i_n_855,pcie_block_i_n_856,pcie_block_i_n_857,pcie_block_i_n_858,pcie_block_i_n_859,pcie_block_i_n_860,pcie_block_i_n_861,pcie_block_i_n_862,pcie_block_i_n_863,pcie_block_i_n_864,pcie_block_i_n_865,pcie_block_i_n_866,pcie_block_i_n_867,pcie_block_i_n_868,pcie_block_i_n_869,pcie_block_i_n_870,pcie_block_i_n_871,pcie_block_i_n_872,pcie_block_i_n_873,pcie_block_i_n_874,pcie_block_i_n_875,pcie_block_i_n_876,pcie_block_i_n_877,pcie_block_i_n_878,pcie_block_i_n_879,pcie_block_i_n_880,pcie_block_i_n_881,pcie_block_i_n_882,pcie_block_i_n_883,pcie_block_i_n_884,pcie_block_i_n_885,pcie_block_i_n_886,pcie_block_i_n_887,pcie_block_i_n_888,pcie_block_i_n_889,pcie_block_i_n_890,pcie_block_i_n_891,pcie_block_i_n_892,pcie_block_i_n_893,pcie_block_i_n_894,pcie_block_i_n_895}),
        .TL2ERRMALFORMED(pcie_block_i_n_158),
        .TL2ERRRXOVERFLOW(pcie_block_i_n_159),
        .TL2PPMSUSPENDOK(pcie_block_i_n_160),
        .TL2PPMSUSPENDREQ(1'b0),
        .TLRSTN(1'b1),
        .TRNFCCPLD(fc_cpld),
        .TRNFCCPLH(fc_cplh),
        .TRNFCNPD(fc_npd),
        .TRNFCNPH(fc_nph),
        .TRNFCPD(fc_pd),
        .TRNFCPH(fc_ph),
        .TRNFCSEL(fc_sel),
        .TRNLNKUP(trn_lnk_up),
        .TRNRBARHIT({pcie_block_i_n_1143,trn_rbar_hit}),
        .TRNRD({trn_rd,pcie_block_i_3}),
        .TRNRDLLPDATA({pcie_block_i_n_896,pcie_block_i_n_897,pcie_block_i_n_898,pcie_block_i_n_899,pcie_block_i_n_900,pcie_block_i_n_901,pcie_block_i_n_902,pcie_block_i_n_903,pcie_block_i_n_904,pcie_block_i_n_905,pcie_block_i_n_906,pcie_block_i_n_907,pcie_block_i_n_908,pcie_block_i_n_909,pcie_block_i_n_910,pcie_block_i_n_911,pcie_block_i_n_912,pcie_block_i_n_913,pcie_block_i_n_914,pcie_block_i_n_915,pcie_block_i_n_916,pcie_block_i_n_917,pcie_block_i_n_918,pcie_block_i_n_919,pcie_block_i_n_920,pcie_block_i_n_921,pcie_block_i_n_922,pcie_block_i_n_923,pcie_block_i_n_924,pcie_block_i_n_925,pcie_block_i_n_926,pcie_block_i_n_927,pcie_block_i_n_928,pcie_block_i_n_929,pcie_block_i_n_930,pcie_block_i_n_931,pcie_block_i_n_932,pcie_block_i_n_933,pcie_block_i_n_934,pcie_block_i_n_935,pcie_block_i_n_936,pcie_block_i_n_937,pcie_block_i_n_938,pcie_block_i_n_939,pcie_block_i_n_940,pcie_block_i_n_941,pcie_block_i_n_942,pcie_block_i_n_943,pcie_block_i_n_944,pcie_block_i_n_945,pcie_block_i_n_946,pcie_block_i_n_947,pcie_block_i_n_948,pcie_block_i_n_949,pcie_block_i_n_950,pcie_block_i_n_951,pcie_block_i_n_952,pcie_block_i_n_953,pcie_block_i_n_954,pcie_block_i_n_955,pcie_block_i_n_956,pcie_block_i_n_957,pcie_block_i_n_958,pcie_block_i_n_959}),
        .TRNRDLLPSRCRDY({pcie_block_i_n_618,pcie_block_i_n_619}),
        .TRNRDSTRDY(trn_rdst_rdy),
        .TRNRECRCERR(trn_recrc_err),
        .TRNREOF(trn_reof),
        .TRNRERRFWD(trn_rerrfwd),
        .TRNRFCPRET(1'b1),
        .TRNRNPOK(rx_np_ok),
        .TRNRNPREQ(rx_np_req),
        .TRNRREM({trn_rrem,pcie_block_i_4}),
        .TRNRSOF(trn_rsof),
        .TRNRSRCDSC(trn_rsrc_dsc),
        .TRNRSRCRDY(trn_rsrc_rdy),
        .TRNTBUFAV(trn_tbuf_av),
        .TRNTCFGGNT(trn_tcfg_gnt),
        .TRNTCFGREQ(trn_tcfg_req),
        .TRNTD({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,trn_td}),
        .TRNTDLLPDATA({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .TRNTDLLPDSTRDY(pcie_block_i_n_169),
        .TRNTDLLPSRCRDY(1'b0),
        .TRNTDSTRDY({NLW_pcie_block_i_TRNTDSTRDY_UNCONNECTED[3:1],trn_tdst_rdy}),
        .TRNTECRCGEN(pcie_block_i_5[0]),
        .TRNTEOF(trn_teof),
        .TRNTERRDROP(tx_err_drop),
        .TRNTERRFWD(pcie_block_i_5[1]),
        .TRNTREM({1'b0,trn_trem}),
        .TRNTSOF(trn_tsof),
        .TRNTSRCDSC(pcie_block_i_5[3]),
        .TRNTSRCRDY(trn_tsrc_rdy),
        .TRNTSTR(pcie_block_i_5[2]),
        .USERCLK(pipe_userclk1_in),
        .USERCLK2(pipe_userclk2_in),
        .USERRSTN(user_rst_n));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_1
       (.I0(cfg_err_atomic_egress_blocked),
        .O(pcie_block_i_i_1_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_10
       (.I0(cfg_err_malformed),
        .O(pcie_block_i_i_10_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_11
       (.I0(cfg_err_mc_blocked),
        .O(pcie_block_i_i_11_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_12
       (.I0(cfg_err_norecovery),
        .O(pcie_block_i_i_12_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_13
       (.I0(cfg_err_poisoned),
        .O(pcie_block_i_i_13_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_14
       (.I0(cfg_err_posted),
        .O(pcie_block_i_i_14_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_15
       (.I0(cfg_err_ur),
        .O(pcie_block_i_i_15_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_16
       (.I0(cfg_interrupt_assert),
        .O(pcie_block_i_i_16_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_17
       (.I0(cfg_interrupt),
        .O(pcie_block_i_i_17_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_18
       (.I0(cfg_interrupt_stat),
        .O(pcie_block_i_i_18_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_19
       (.I0(cfg_mgmt_rd_en),
        .O(pcie_block_i_i_19_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_2
       (.I0(cfg_err_cor),
        .O(pcie_block_i_i_2_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_20
       (.I0(cfg_mgmt_wr_en),
        .O(pcie_block_i_i_20_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_21
       (.I0(cfg_mgmt_wr_readonly),
        .O(pcie_block_i_i_21_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_22
       (.I0(cfg_mgmt_wr_rw1c_as_rw),
        .O(pcie_block_i_i_22_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_23
       (.I0(cfg_pm_force_state_en),
        .O(pcie_block_i_i_23_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_24
       (.I0(cfg_pm_halt_aspm_l0s),
        .O(pcie_block_i_i_24_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_25
       (.I0(cfg_pm_halt_aspm_l1),
        .O(pcie_block_i_i_25_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_27
       (.I0(cfg_pm_wake),
        .O(pcie_block_i_i_27_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_28
       (.I0(cfg_trn_pending),
        .O(pcie_block_i_i_28_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_3
       (.I0(cfg_err_cpl_abort),
        .O(pcie_block_i_i_3_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_4
       (.I0(cfg_err_cpl_timeout),
        .O(pcie_block_i_i_4_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_5
       (.I0(cfg_err_cpl_unexpect),
        .O(pcie_block_i_i_5_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_6
       (.I0(cfg_err_ecrc),
        .O(pcie_block_i_i_6_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_7
       (.I0(cfg_err_internal_cor),
        .O(pcie_block_i_i_7_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_8
       (.I0(cfg_err_internal_uncor),
        .O(pcie_block_i_i_8_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    pcie_block_i_i_9
       (.I0(cfg_err_locked),
        .O(pcie_block_i_i_9_n_0));
  pcie_7x_bridge_pcie_bram_top_7x pcie_bram_top
       (.MIMRXRADDR(mim_rx_raddr[10:0]),
        .MIMRXWADDR(mim_rx_waddr[10:0]),
        .MIMTXRADDR(mim_tx_raddr[10:0]),
        .MIMTXWADDR(mim_tx_waddr[10:0]),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (mim_rx_rdata),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (mim_rx_wdata),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(mim_tx_rdata),
        .wdata(mim_tx_wdata));
  LUT1 #(
    .INIT(2'h1)) 
    phy_lnk_up_cdc_i_1
       (.I0(pl_phy_lnk_up_n),
        .O(src_in));
  LUT5 #(
    .INIT(32'hFFFEAAAA)) 
    ppm_L1_thrtl_i_1
       (.I0(ppm_L1_trig),
        .I1(cfg_pcie_link_state[0]),
        .I2(cfg_pcie_link_state[2]),
        .I3(cfg_pcie_link_state[1]),
        .I4(ppm_L1_thrtl),
        .O(pcie_block_i_0));
  LUT5 #(
    .INIT(32'h00000001)) 
    tbuf_av_min_thrtl_i_1
       (.I0(trn_tbuf_av[5]),
        .I1(trn_tbuf_av[4]),
        .I2(trn_tbuf_av[3]),
        .I3(trn_tbuf_av[2]),
        .I4(trn_tbuf_av[1]),
        .O(tbuf_av_min_trig));
  LUT6 #(
    .INIT(64'h0000000100010001)) 
    tready_thrtl_i_11
       (.I0(trn_tbuf_av[5]),
        .I1(trn_tbuf_av[4]),
        .I2(trn_tbuf_av[3]),
        .I3(trn_tbuf_av[2]),
        .I4(trn_tbuf_av[0]),
        .I5(trn_tbuf_av[1]),
        .O(pcie_block_i_1));
  LUT2 #(
    .INIT(4'h8)) 
    tready_thrtl_i_9
       (.I0(trn_tcfg_req),
        .I1(reg_tcfg_gnt),
        .O(tcfg_req_trig));
  LUT6 #(
    .INIT(64'h08000000AEAA2AAA)) 
    trn_in_packet_i_1
       (.I0(trn_in_packet),
        .I1(trn_rdst_rdy),
        .I2(trn_reof),
        .I3(trn_rsrc_rdy),
        .I4(trn_rsof),
        .I5(trn_rsrc_dsc),
        .O(trn_in_packet_reg));
  (* SOFT_HLUTNM = "soft_lutpair108" *) 
  LUT2 #(
    .INIT(4'hE)) 
    trn_rsrc_dsc_prev_i_1
       (.I0(trn_rsrc_dsc),
        .I1(reg_dsc_detect),
        .O(trn_rsrc_dsc_prev0));
  (* SOFT_HLUTNM = "soft_lutpair108" *) 
  LUT4 #(
    .INIT(16'hAA08)) 
    trn_rsrc_rdy_prev_i_1
       (.I0(trn_rsrc_rdy),
        .I1(trn_rsof),
        .I2(trn_rsrc_dsc),
        .I3(trn_in_packet),
        .O(rsrc_rdy_filtered));
  LUT3 #(
    .INIT(8'h2A)) 
    user_reset_int_i_1
       (.I0(bridge_reset_int),
        .I1(pl_phy_lnk_up),
        .I2(user_rst_n),
        .O(user_reset_int_reg));
endmodule

module pcie_7x_bridge_pcie_bram_7x
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_6 \use_tdp.ramb36 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata),
        .wdata(wdata));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_1
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_5 \use_tdp.ramb36 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata),
        .wdata(wdata));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_10
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_11 \use_tdp.ramb36 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_2
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_4 \use_tdp.ramb36 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata),
        .wdata(wdata));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_3
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [14:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [14:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [14:0]rdata;
  wire [14:0]wdata;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO \use_tdp.ramb36 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata),
        .wdata(wdata));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_7
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_14 \use_tdp.ramb36 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_8
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_13 \use_tdp.ramb36 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_bram_7x" *) 
module pcie_7x_bridge_pcie_bram_7x_9
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;

  pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_12 \use_tdp.ramb36 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
endmodule

module pcie_7x_bridge_pcie_bram_top_7x
   (rdata,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [68:0]rdata;
  output [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [68:0]wdata;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [68:0]rdata;
  wire [68:0]wdata;

  pcie_7x_bridge_pcie_brams_7x pcie_brams_rx
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
  pcie_7x_bridge_pcie_brams_7x_0 pcie_brams_tx
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata),
        .wdata(wdata));
endmodule

module pcie_7x_bridge_pcie_brams_7x
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 );
  output [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl ;
  wire [67:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;

  pcie_7x_bridge_pcie_bram_7x_7 \brams[0].ram 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl [17:0]),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [17:0]),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
  pcie_7x_bridge_pcie_bram_7x_8 \brams[1].ram 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl [35:18]),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [35:18]),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
  pcie_7x_bridge_pcie_bram_7x_9 \brams[2].ram 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl [53:36]),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [53:36]),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
  pcie_7x_bridge_pcie_bram_7x_10 \brams[3].ram 
       (.MIMRXRADDR(MIMRXRADDR),
        .MIMRXWADDR(MIMRXWADDR),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl [67:54]),
        .\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [67:54]),
        .mim_rx_ren(mim_rx_ren),
        .mim_rx_wen(mim_rx_wen),
        .pipe_userclk1_in(pipe_userclk1_in));
endmodule

(* ORIG_REF_NAME = "pcie_7x_bridge_pcie_brams_7x" *) 
module pcie_7x_bridge_pcie_brams_7x_0
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [68:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [68:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [68:0]rdata;
  wire [68:0]wdata;

  pcie_7x_bridge_pcie_bram_7x \brams[0].ram 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata[17:0]),
        .wdata(wdata[17:0]));
  pcie_7x_bridge_pcie_bram_7x_1 \brams[1].ram 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata[35:18]),
        .wdata(wdata[35:18]));
  pcie_7x_bridge_pcie_bram_7x_2 \brams[2].ram 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata[53:36]),
        .wdata(wdata[53:36]));
  pcie_7x_bridge_pcie_bram_7x_3 \brams[3].ram 
       (.MIMTXRADDR(MIMTXRADDR),
        .MIMTXWADDR(MIMTXWADDR),
        .mim_tx_ren(mim_tx_ren),
        .mim_tx_wen(mim_tx_wen),
        .pipe_userclk1_in(pipe_userclk1_in),
        .rdata(rdata[68:54]),
        .wdata(wdata[68:54]));
endmodule

module pcie_7x_bridge_pcie_top
   (m_axis_rx_tvalid_reg,
    m_axis_rx_tkeep,
    m_axis_rx_tlast,
    trn_tcfg_req,
    tready_thrtl_reg,
    user_reset_int_reg,
    src_in,
    cfg_mgmt_rd_wr_done,
    cfg_err_aer_headerlog_set,
    cfg_err_cpl_rdy,
    cfg_interrupt_rdy,
    cfg_msg_received,
    cfg_received_func_lvl_rst,
    cfg_pcie_link_state,
    m_axis_rx_tdata,
    m_axis_rx_tuser,
    trn_tbuf_av,
    cfg_to_turnoff,
    cfg_bus_number,
    cfg_msg_data,
    cfg_device_number,
    cfg_function_number,
    cfg_aer_ecrc_check_en,
    cfg_aer_ecrc_gen_en,
    cfg_aer_rooterr_corr_err_received,
    cfg_aer_rooterr_corr_err_reporting_en,
    cfg_aer_rooterr_fatal_err_received,
    cfg_aer_rooterr_fatal_err_reporting_en,
    cfg_aer_rooterr_non_fatal_err_received,
    cfg_aer_rooterr_non_fatal_err_reporting_en,
    cfg_bridge_serr_en,
    cfg_command,
    cfg_dcommand2,
    cfg_dcommand,
    cfg_dstatus,
    cfg_interrupt_msienable,
    cfg_interrupt_msixenable,
    cfg_interrupt_msixfm,
    cfg_lcommand,
    cfg_lstatus,
    cfg_msg_received_assert_int_a,
    cfg_msg_received_assert_int_b,
    cfg_msg_received_assert_int_c,
    cfg_msg_received_assert_int_d,
    cfg_msg_received_deassert_int_a,
    cfg_msg_received_deassert_int_b,
    cfg_msg_received_deassert_int_c,
    cfg_msg_received_deassert_int_d,
    cfg_msg_received_err_cor,
    cfg_msg_received_err_fatal,
    cfg_msg_received_err_non_fatal,
    cfg_msg_received_pm_as_nak,
    cfg_msg_received_pme_to_ack,
    cfg_msg_received_pm_pme,
    cfg_msg_received_setslotpowerlimit,
    cfg_pmcsr_pme_en,
    cfg_pmcsr_pme_status,
    cfg_root_control_pme_int_en,
    cfg_root_control_syserr_corr_err_en,
    cfg_root_control_syserr_fatal_err_en,
    cfg_root_control_syserr_non_fatal_err_en,
    cfg_slot_control_electromech_il_ctl_pulse,
    pcie_drp_rdy,
    pipe_rx0_polarity,
    pipe_tx0_compliance,
    pipe_tx0_elec_idle,
    pipe_tx_deemph,
    pipe_tx_rate,
    pipe_tx_rcvr_det,
    pl_directed_change_done,
    pl_link_gen2_cap,
    pl_link_partner_gen2_supported,
    pl_link_upcfg_cap,
    pl_received_hot_rst,
    pl_sel_lnk_rate,
    trn_lnk_up,
    tx_err_drop,
    fc_cpld,
    fc_npd,
    fc_pd,
    pcie_drp_do,
    pipe_tx0_data,
    cfg_pmcsr_powerstate,
    pipe_tx0_char_is_k,
    pipe_tx0_powerdown,
    pl_lane_reversal_mode,
    pl_rx_pm_state,
    pl_sel_lnk_width,
    cfg_interrupt_mmenable,
    pipe_tx_margin,
    pl_initial_link_width,
    pl_tx_pm_state,
    cfg_mgmt_do,
    pl_ltssm_state,
    cfg_vc_tcvc_map,
    cfg_interrupt_do,
    fc_cplh,
    fc_nph,
    fc_ph,
    SR,
    pipe_userclk2_in,
    tx_cfg_gnt,
    cfg_turnoff_ok,
    s_axis_tx_tlast,
    s_axis_tx_tvalid,
    s_axis_tx_tkeep,
    m_axis_rx_tready,
    bridge_reset_int,
    pl_phy_lnk_up,
    cfg_trn_pending,
    out,
    cfg_mgmt_wr_rw1c_as_rw,
    cfg_mgmt_wr_readonly,
    cfg_mgmt_wr_en,
    cfg_mgmt_rd_en,
    cfg_err_malformed,
    cfg_err_cor,
    cfg_err_ur,
    cfg_err_ecrc,
    cfg_err_cpl_timeout,
    cfg_err_cpl_abort,
    cfg_err_cpl_unexpect,
    cfg_err_poisoned,
    cfg_err_atomic_egress_blocked,
    cfg_err_mc_blocked,
    cfg_err_internal_uncor,
    cfg_err_internal_cor,
    cfg_err_posted,
    cfg_err_locked,
    cfg_err_norecovery,
    cfg_interrupt,
    cfg_interrupt_assert,
    cfg_interrupt_stat,
    cfg_pm_halt_aspm_l0s,
    cfg_pm_halt_aspm_l1,
    cfg_pm_force_state_en,
    cfg_pm_wake,
    s_axis_tx_tdata,
    s_axis_tx_tuser,
    pipe_userclk1_in,
    pcie_drp_clk,
    pcie_drp_en,
    pcie_drp_we,
    pipe_pclk_in,
    pipe_rx0_chanisaligned,
    pipe_rx0_elec_idle,
    pipe_rx0_phy_status,
    pipe_rx0_valid,
    pl_directed_link_auton,
    pl_directed_link_speed,
    pl_downstream_deemph_source,
    pl_transmit_hot_rst,
    pl_upstream_prefer_deemph,
    sys_rst_n,
    rx_np_ok,
    rx_np_req,
    cfg_err_aer_headerlog,
    pcie_drp_di,
    pipe_rx0_data,
    cfg_pm_force_state,
    pipe_rx0_char_is_k,
    pl_directed_link_change,
    pl_directed_link_width,
    cfg_ds_function_number,
    pipe_rx0_status,
    fc_sel,
    cfg_mgmt_di,
    cfg_mgmt_byte_en_n,
    cfg_err_tlp_cpl_header,
    cfg_aer_interrupt_msgnum,
    cfg_ds_device_number,
    cfg_pciecap_interrupt_msgnum,
    cfg_dsn,
    cfg_ds_bus_number,
    cfg_interrupt_di,
    pcie_drp_addr,
    cfg_mgmt_dwaddr);
  output m_axis_rx_tvalid_reg;
  output [0:0]m_axis_rx_tkeep;
  output m_axis_rx_tlast;
  output trn_tcfg_req;
  output tready_thrtl_reg;
  output user_reset_int_reg;
  output src_in;
  output cfg_mgmt_rd_wr_done;
  output cfg_err_aer_headerlog_set;
  output cfg_err_cpl_rdy;
  output cfg_interrupt_rdy;
  output cfg_msg_received;
  output cfg_received_func_lvl_rst;
  output [2:0]cfg_pcie_link_state;
  output [63:0]m_axis_rx_tdata;
  output [12:0]m_axis_rx_tuser;
  output [5:0]trn_tbuf_av;
  output cfg_to_turnoff;
  output [7:0]cfg_bus_number;
  output [15:0]cfg_msg_data;
  output [4:0]cfg_device_number;
  output [2:0]cfg_function_number;
  output cfg_aer_ecrc_check_en;
  output cfg_aer_ecrc_gen_en;
  output cfg_aer_rooterr_corr_err_received;
  output cfg_aer_rooterr_corr_err_reporting_en;
  output cfg_aer_rooterr_fatal_err_received;
  output cfg_aer_rooterr_fatal_err_reporting_en;
  output cfg_aer_rooterr_non_fatal_err_received;
  output cfg_aer_rooterr_non_fatal_err_reporting_en;
  output cfg_bridge_serr_en;
  output [4:0]cfg_command;
  output [11:0]cfg_dcommand2;
  output [14:0]cfg_dcommand;
  output [3:0]cfg_dstatus;
  output cfg_interrupt_msienable;
  output cfg_interrupt_msixenable;
  output cfg_interrupt_msixfm;
  output [10:0]cfg_lcommand;
  output [9:0]cfg_lstatus;
  output cfg_msg_received_assert_int_a;
  output cfg_msg_received_assert_int_b;
  output cfg_msg_received_assert_int_c;
  output cfg_msg_received_assert_int_d;
  output cfg_msg_received_deassert_int_a;
  output cfg_msg_received_deassert_int_b;
  output cfg_msg_received_deassert_int_c;
  output cfg_msg_received_deassert_int_d;
  output cfg_msg_received_err_cor;
  output cfg_msg_received_err_fatal;
  output cfg_msg_received_err_non_fatal;
  output cfg_msg_received_pm_as_nak;
  output cfg_msg_received_pme_to_ack;
  output cfg_msg_received_pm_pme;
  output cfg_msg_received_setslotpowerlimit;
  output cfg_pmcsr_pme_en;
  output cfg_pmcsr_pme_status;
  output cfg_root_control_pme_int_en;
  output cfg_root_control_syserr_corr_err_en;
  output cfg_root_control_syserr_fatal_err_en;
  output cfg_root_control_syserr_non_fatal_err_en;
  output cfg_slot_control_electromech_il_ctl_pulse;
  output pcie_drp_rdy;
  output pipe_rx0_polarity;
  output pipe_tx0_compliance;
  output pipe_tx0_elec_idle;
  output pipe_tx_deemph;
  output pipe_tx_rate;
  output pipe_tx_rcvr_det;
  output pl_directed_change_done;
  output pl_link_gen2_cap;
  output pl_link_partner_gen2_supported;
  output pl_link_upcfg_cap;
  output pl_received_hot_rst;
  output pl_sel_lnk_rate;
  output trn_lnk_up;
  output tx_err_drop;
  output [11:0]fc_cpld;
  output [11:0]fc_npd;
  output [11:0]fc_pd;
  output [15:0]pcie_drp_do;
  output [15:0]pipe_tx0_data;
  output [1:0]cfg_pmcsr_powerstate;
  output [1:0]pipe_tx0_char_is_k;
  output [1:0]pipe_tx0_powerdown;
  output [1:0]pl_lane_reversal_mode;
  output [1:0]pl_rx_pm_state;
  output [1:0]pl_sel_lnk_width;
  output [2:0]cfg_interrupt_mmenable;
  output [2:0]pipe_tx_margin;
  output [2:0]pl_initial_link_width;
  output [2:0]pl_tx_pm_state;
  output [31:0]cfg_mgmt_do;
  output [5:0]pl_ltssm_state;
  output [6:0]cfg_vc_tcvc_map;
  output [7:0]cfg_interrupt_do;
  output [7:0]fc_cplh;
  output [7:0]fc_nph;
  output [7:0]fc_ph;
  input [0:0]SR;
  input pipe_userclk2_in;
  input tx_cfg_gnt;
  input cfg_turnoff_ok;
  input s_axis_tx_tlast;
  input s_axis_tx_tvalid;
  input [0:0]s_axis_tx_tkeep;
  input m_axis_rx_tready;
  input bridge_reset_int;
  input pl_phy_lnk_up;
  input cfg_trn_pending;
  input out;
  input cfg_mgmt_wr_rw1c_as_rw;
  input cfg_mgmt_wr_readonly;
  input cfg_mgmt_wr_en;
  input cfg_mgmt_rd_en;
  input cfg_err_malformed;
  input cfg_err_cor;
  input cfg_err_ur;
  input cfg_err_ecrc;
  input cfg_err_cpl_timeout;
  input cfg_err_cpl_abort;
  input cfg_err_cpl_unexpect;
  input cfg_err_poisoned;
  input cfg_err_atomic_egress_blocked;
  input cfg_err_mc_blocked;
  input cfg_err_internal_uncor;
  input cfg_err_internal_cor;
  input cfg_err_posted;
  input cfg_err_locked;
  input cfg_err_norecovery;
  input cfg_interrupt;
  input cfg_interrupt_assert;
  input cfg_interrupt_stat;
  input cfg_pm_halt_aspm_l0s;
  input cfg_pm_halt_aspm_l1;
  input cfg_pm_force_state_en;
  input cfg_pm_wake;
  input [63:0]s_axis_tx_tdata;
  input [3:0]s_axis_tx_tuser;
  input pipe_userclk1_in;
  input pcie_drp_clk;
  input pcie_drp_en;
  input pcie_drp_we;
  input pipe_pclk_in;
  input pipe_rx0_chanisaligned;
  input pipe_rx0_elec_idle;
  input pipe_rx0_phy_status;
  input pipe_rx0_valid;
  input pl_directed_link_auton;
  input pl_directed_link_speed;
  input pl_downstream_deemph_source;
  input pl_transmit_hot_rst;
  input pl_upstream_prefer_deemph;
  input sys_rst_n;
  input rx_np_ok;
  input rx_np_req;
  input [127:0]cfg_err_aer_headerlog;
  input [15:0]pcie_drp_di;
  input [15:0]pipe_rx0_data;
  input [1:0]cfg_pm_force_state;
  input [1:0]pipe_rx0_char_is_k;
  input [1:0]pl_directed_link_change;
  input [1:0]pl_directed_link_width;
  input [2:0]cfg_ds_function_number;
  input [2:0]pipe_rx0_status;
  input [2:0]fc_sel;
  input [31:0]cfg_mgmt_di;
  input [3:0]cfg_mgmt_byte_en_n;
  input [47:0]cfg_err_tlp_cpl_header;
  input [4:0]cfg_aer_interrupt_msgnum;
  input [4:0]cfg_ds_device_number;
  input [4:0]cfg_pciecap_interrupt_msgnum;
  input [63:0]cfg_dsn;
  input [7:0]cfg_ds_bus_number;
  input [7:0]cfg_interrupt_di;
  input [8:0]pcie_drp_addr;
  input [9:0]cfg_mgmt_dwaddr;

  wire [0:0]SR;
  wire bridge_reset_int;
  wire cfg_aer_ecrc_check_en;
  wire cfg_aer_ecrc_gen_en;
  wire [4:0]cfg_aer_interrupt_msgnum;
  wire cfg_aer_rooterr_corr_err_received;
  wire cfg_aer_rooterr_corr_err_reporting_en;
  wire cfg_aer_rooterr_fatal_err_received;
  wire cfg_aer_rooterr_fatal_err_reporting_en;
  wire cfg_aer_rooterr_non_fatal_err_received;
  wire cfg_aer_rooterr_non_fatal_err_reporting_en;
  wire cfg_bridge_serr_en;
  wire [7:0]cfg_bus_number;
  wire [4:0]cfg_command;
  wire [14:0]cfg_dcommand;
  wire [11:0]cfg_dcommand2;
  wire [4:0]cfg_device_number;
  wire [7:0]cfg_ds_bus_number;
  wire [4:0]cfg_ds_device_number;
  wire [2:0]cfg_ds_function_number;
  wire [63:0]cfg_dsn;
  wire [3:0]cfg_dstatus;
  wire [127:0]cfg_err_aer_headerlog;
  wire cfg_err_aer_headerlog_set;
  wire cfg_err_atomic_egress_blocked;
  wire cfg_err_cor;
  wire cfg_err_cpl_abort;
  wire cfg_err_cpl_rdy;
  wire cfg_err_cpl_timeout;
  wire cfg_err_cpl_unexpect;
  wire cfg_err_ecrc;
  wire cfg_err_internal_cor;
  wire cfg_err_internal_uncor;
  wire cfg_err_locked;
  wire cfg_err_malformed;
  wire cfg_err_mc_blocked;
  wire cfg_err_norecovery;
  wire cfg_err_poisoned;
  wire cfg_err_posted;
  wire [47:0]cfg_err_tlp_cpl_header;
  wire cfg_err_ur;
  wire [2:0]cfg_function_number;
  wire cfg_interrupt;
  wire cfg_interrupt_assert;
  wire [7:0]cfg_interrupt_di;
  wire [7:0]cfg_interrupt_do;
  wire [2:0]cfg_interrupt_mmenable;
  wire cfg_interrupt_msienable;
  wire cfg_interrupt_msixenable;
  wire cfg_interrupt_msixfm;
  wire cfg_interrupt_rdy;
  wire cfg_interrupt_stat;
  wire [10:0]cfg_lcommand;
  wire [9:0]cfg_lstatus;
  wire [3:0]cfg_mgmt_byte_en_n;
  wire [31:0]cfg_mgmt_di;
  wire [31:0]cfg_mgmt_do;
  wire [9:0]cfg_mgmt_dwaddr;
  wire cfg_mgmt_rd_en;
  wire cfg_mgmt_rd_wr_done;
  wire cfg_mgmt_wr_en;
  wire cfg_mgmt_wr_readonly;
  wire cfg_mgmt_wr_rw1c_as_rw;
  wire [15:0]cfg_msg_data;
  wire cfg_msg_received;
  wire cfg_msg_received_assert_int_a;
  wire cfg_msg_received_assert_int_b;
  wire cfg_msg_received_assert_int_c;
  wire cfg_msg_received_assert_int_d;
  wire cfg_msg_received_deassert_int_a;
  wire cfg_msg_received_deassert_int_b;
  wire cfg_msg_received_deassert_int_c;
  wire cfg_msg_received_deassert_int_d;
  wire cfg_msg_received_err_cor;
  wire cfg_msg_received_err_fatal;
  wire cfg_msg_received_err_non_fatal;
  wire cfg_msg_received_pm_as_nak;
  wire cfg_msg_received_pm_pme;
  wire cfg_msg_received_pme_to_ack;
  wire cfg_msg_received_setslotpowerlimit;
  wire [2:0]cfg_pcie_link_state;
  wire [4:0]cfg_pciecap_interrupt_msgnum;
  wire [1:0]cfg_pm_force_state;
  wire cfg_pm_force_state_en;
  wire cfg_pm_halt_aspm_l0s;
  wire cfg_pm_halt_aspm_l1;
  wire cfg_pm_wake;
  wire cfg_pmcsr_pme_en;
  wire cfg_pmcsr_pme_status;
  wire [1:0]cfg_pmcsr_powerstate;
  wire cfg_received_func_lvl_rst;
  wire cfg_root_control_pme_int_en;
  wire cfg_root_control_syserr_corr_err_en;
  wire cfg_root_control_syserr_fatal_err_en;
  wire cfg_root_control_syserr_non_fatal_err_en;
  wire cfg_slot_control_electromech_il_ctl_pulse;
  wire cfg_to_turnoff;
  wire cfg_trn_pending;
  wire cfg_turnoff_ok;
  wire cfg_turnoff_ok_w;
  wire [6:0]cfg_vc_tcvc_map;
  wire [11:0]fc_cpld;
  wire [7:0]fc_cplh;
  wire [11:0]fc_npd;
  wire [7:0]fc_nph;
  wire [11:0]fc_pd;
  wire [7:0]fc_ph;
  wire [2:0]fc_sel;
  wire [63:0]m_axis_rx_tdata;
  wire [0:0]m_axis_rx_tkeep;
  wire m_axis_rx_tlast;
  wire m_axis_rx_tready;
  wire [12:0]m_axis_rx_tuser;
  wire m_axis_rx_tvalid_reg;
  wire out;
  wire pcie_7x_i_n_13;
  wire pcie_7x_i_n_22;
  wire pcie_7x_i_n_30;
  wire pcie_7x_i_n_6;
  wire pcie_7x_i_n_9;
  wire [8:0]pcie_drp_addr;
  wire pcie_drp_clk;
  wire [15:0]pcie_drp_di;
  wire [15:0]pcie_drp_do;
  wire pcie_drp_en;
  wire pcie_drp_rdy;
  wire pcie_drp_we;
  wire pipe_pclk_in;
  wire pipe_rx0_chanisaligned;
  wire [1:0]pipe_rx0_char_is_k;
  wire [15:0]pipe_rx0_data;
  wire pipe_rx0_elec_idle;
  wire pipe_rx0_phy_status;
  wire pipe_rx0_polarity;
  wire [2:0]pipe_rx0_status;
  wire pipe_rx0_valid;
  wire [1:0]pipe_tx0_char_is_k;
  wire pipe_tx0_compliance;
  wire [15:0]pipe_tx0_data;
  wire pipe_tx0_elec_idle;
  wire [1:0]pipe_tx0_powerdown;
  wire pipe_tx_deemph;
  wire [2:0]pipe_tx_margin;
  wire pipe_tx_rate;
  wire pipe_tx_rcvr_det;
  wire pipe_userclk1_in;
  wire pipe_userclk2_in;
  wire pl_directed_change_done;
  wire pl_directed_link_auton;
  wire [1:0]pl_directed_link_change;
  wire pl_directed_link_speed;
  wire [1:0]pl_directed_link_width;
  wire pl_downstream_deemph_source;
  wire [2:0]pl_initial_link_width;
  wire [1:0]pl_lane_reversal_mode;
  wire pl_link_gen2_cap;
  wire pl_link_partner_gen2_supported;
  wire pl_link_upcfg_cap;
  wire [5:0]pl_ltssm_state;
  wire pl_phy_lnk_up;
  wire pl_received_hot_rst;
  wire [1:0]pl_rx_pm_state;
  wire pl_sel_lnk_rate;
  wire [1:0]pl_sel_lnk_width;
  wire pl_transmit_hot_rst;
  wire [2:0]pl_tx_pm_state;
  wire pl_upstream_prefer_deemph;
  wire \rx_inst/rx_pipeline_inst/dsc_detect ;
  wire \rx_inst/rx_pipeline_inst/reg_dsc_detect ;
  wire \rx_inst/rx_pipeline_inst/rsrc_rdy_filtered ;
  wire \rx_inst/rx_pipeline_inst/trn_in_packet ;
  wire \rx_inst/rx_pipeline_inst/trn_rsrc_dsc_d ;
  wire \rx_inst/rx_pipeline_inst/trn_rsrc_dsc_prev0 ;
  wire rx_np_ok;
  wire rx_np_req;
  wire [63:0]s_axis_tx_tdata;
  wire [0:0]s_axis_tx_tkeep;
  wire s_axis_tx_tlast;
  wire [3:0]s_axis_tx_tuser;
  wire s_axis_tx_tvalid;
  wire src_in;
  wire sys_rst_n;
  wire tready_thrtl_reg;
  wire trn_lnk_up;
  wire [6:0]trn_rbar_hit;
  wire [63:0]trn_rd;
  wire trn_rdst_rdy;
  wire trn_recrc_err;
  wire trn_reof;
  wire trn_rerrfwd;
  wire [0:0]trn_rrem;
  wire trn_rsof;
  wire trn_rsrc_dsc;
  wire [5:0]trn_tbuf_av;
  wire trn_tcfg_gnt;
  wire trn_tcfg_req;
  wire [63:0]trn_td;
  wire trn_tdst_rdy;
  wire trn_tecrc_gen;
  wire trn_teof;
  wire trn_terrfwd;
  wire trn_trem;
  wire trn_tsof;
  wire trn_tsrc_dsc;
  wire trn_tsrc_rdy;
  wire trn_tstr;
  wire tx_cfg_gnt;
  wire tx_err_drop;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/lnk_up_thrtl ;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_thrtl ;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_trig ;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/reg_tcfg_gnt ;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tbuf_av_min_trig ;
  wire \tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tcfg_req_trig ;
  wire \tx_inst/tx_pipeline_inst/reg_disable_trn2 ;
  wire user_reset_int_reg;

  pcie_7x_bridge_axi_basic_top axi_basic_top
       (.E(trn_rdst_rdy),
        .Q(m_axis_rx_tdata),
        .SR(SR),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pm_turnoff_ok_n(cfg_turnoff_ok_w),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_turnoff_ok(cfg_turnoff_ok),
        .dsc_detect(\rx_inst/rx_pipeline_inst/dsc_detect ),
        .lnk_up_thrtl(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/lnk_up_thrtl ),
        .lnk_up_thrtl_reg(pcie_7x_i_n_30),
        .m_axis_rx_tkeep(m_axis_rx_tkeep),
        .m_axis_rx_tlast(m_axis_rx_tlast),
        .m_axis_rx_tready(m_axis_rx_tready),
        .m_axis_rx_tuser(m_axis_rx_tuser),
        .m_axis_rx_tvalid_reg(m_axis_rx_tvalid_reg),
        .out(out),
        .pipe_userclk2_in(pipe_userclk2_in),
        .ppm_L1_thrtl(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_thrtl ),
        .ppm_L1_thrtl_reg(pcie_7x_i_n_13),
        .ppm_L1_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_trig ),
        .reg_dsc_detect(\rx_inst/rx_pipeline_inst/reg_dsc_detect ),
        .reg_tcfg_gnt(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/reg_tcfg_gnt ),
        .rsrc_rdy_filtered(\rx_inst/rx_pipeline_inst/rsrc_rdy_filtered ),
        .s_axis_tx_tdata(s_axis_tx_tdata),
        .s_axis_tx_tkeep(s_axis_tx_tkeep),
        .s_axis_tx_tlast(s_axis_tx_tlast),
        .s_axis_tx_tuser(s_axis_tx_tuser),
        .s_axis_tx_tvalid(s_axis_tx_tvalid),
        .tbuf_av_min_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tbuf_av_min_trig ),
        .tcfg_req_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tcfg_req_trig ),
        .\throttle_ctl_pipeline.reg_tdata_reg[63] ({trn_td[31:0],trn_td[63:32]}),
        .\throttle_ctl_pipeline.reg_tuser_reg[3] ({trn_tsrc_dsc,trn_tstr,trn_terrfwd,trn_tecrc_gen}),
        .tready_thrtl_i_5(pcie_7x_i_n_22),
        .tready_thrtl_reg(tready_thrtl_reg),
        .trn_in_packet(\rx_inst/rx_pipeline_inst/trn_in_packet ),
        .trn_in_packet_reg(pcie_7x_i_n_9),
        .trn_rbar_hit(trn_rbar_hit),
        .trn_rd(trn_rd),
        .trn_recrc_err(trn_recrc_err),
        .trn_reof(trn_reof),
        .trn_rerrfwd(trn_rerrfwd),
        .trn_rrem(trn_rrem),
        .trn_rsof(trn_rsof),
        .trn_rsrc_dsc(trn_rsrc_dsc),
        .trn_rsrc_dsc_d(\rx_inst/rx_pipeline_inst/trn_rsrc_dsc_d ),
        .trn_rsrc_dsc_prev0(\rx_inst/rx_pipeline_inst/trn_rsrc_dsc_prev0 ),
        .trn_tbuf_av(trn_tbuf_av),
        .trn_tcfg_gnt(trn_tcfg_gnt),
        .trn_tcfg_req(trn_tcfg_req),
        .trn_tdst_rdy(trn_tdst_rdy),
        .trn_teof(trn_teof),
        .trn_trem(trn_trem),
        .trn_tsof(trn_tsof),
        .trn_tsrc_rdy(trn_tsrc_rdy),
        .tx_cfg_gnt(tx_cfg_gnt));
  LUT1 #(
    .INIT(2'h1)) 
    \cfg_bus_number_d[7]_i_1 
       (.I0(out),
        .O(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[8]),
        .Q(cfg_bus_number[0]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[9]),
        .Q(cfg_bus_number[1]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[10]),
        .Q(cfg_bus_number[2]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[11]),
        .Q(cfg_bus_number[3]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[12]),
        .Q(cfg_bus_number[4]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[5] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[13]),
        .Q(cfg_bus_number[5]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[6] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[14]),
        .Q(cfg_bus_number[6]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_bus_number_d_reg[7] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[15]),
        .Q(cfg_bus_number[7]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_device_number_d_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[3]),
        .Q(cfg_device_number[0]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_device_number_d_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[4]),
        .Q(cfg_device_number[1]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_device_number_d_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[5]),
        .Q(cfg_device_number[2]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_device_number_d_reg[3] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[6]),
        .Q(cfg_device_number[3]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_device_number_d_reg[4] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[7]),
        .Q(cfg_device_number[4]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_function_number_d_reg[0] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[0]),
        .Q(cfg_function_number[0]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_function_number_d_reg[1] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[1]),
        .Q(cfg_function_number[1]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  FDRE \cfg_function_number_d_reg[2] 
       (.C(pipe_userclk2_in),
        .CE(pcie_7x_i_n_6),
        .D(cfg_msg_data[2]),
        .Q(cfg_function_number[2]),
        .R(\tx_inst/tx_pipeline_inst/reg_disable_trn2 ));
  pcie_7x_bridge_pcie_7x pcie_7x_i
       (.E(pcie_7x_i_n_6),
        .bridge_reset_int(bridge_reset_int),
        .cfg_aer_ecrc_check_en(cfg_aer_ecrc_check_en),
        .cfg_aer_ecrc_gen_en(cfg_aer_ecrc_gen_en),
        .cfg_aer_interrupt_msgnum(cfg_aer_interrupt_msgnum),
        .cfg_aer_rooterr_corr_err_received(cfg_aer_rooterr_corr_err_received),
        .cfg_aer_rooterr_corr_err_reporting_en(cfg_aer_rooterr_corr_err_reporting_en),
        .cfg_aer_rooterr_fatal_err_received(cfg_aer_rooterr_fatal_err_received),
        .cfg_aer_rooterr_fatal_err_reporting_en(cfg_aer_rooterr_fatal_err_reporting_en),
        .cfg_aer_rooterr_non_fatal_err_received(cfg_aer_rooterr_non_fatal_err_received),
        .cfg_aer_rooterr_non_fatal_err_reporting_en(cfg_aer_rooterr_non_fatal_err_reporting_en),
        .cfg_bridge_serr_en(cfg_bridge_serr_en),
        .cfg_command(cfg_command),
        .cfg_dcommand(cfg_dcommand),
        .cfg_dcommand2(cfg_dcommand2),
        .cfg_ds_bus_number(cfg_ds_bus_number),
        .cfg_ds_device_number(cfg_ds_device_number),
        .cfg_ds_function_number(cfg_ds_function_number),
        .cfg_dsn(cfg_dsn),
        .cfg_dstatus(cfg_dstatus),
        .cfg_err_aer_headerlog(cfg_err_aer_headerlog),
        .cfg_err_aer_headerlog_set(cfg_err_aer_headerlog_set),
        .cfg_err_atomic_egress_blocked(cfg_err_atomic_egress_blocked),
        .cfg_err_cor(cfg_err_cor),
        .cfg_err_cpl_abort(cfg_err_cpl_abort),
        .cfg_err_cpl_rdy(cfg_err_cpl_rdy),
        .cfg_err_cpl_timeout(cfg_err_cpl_timeout),
        .cfg_err_cpl_unexpect(cfg_err_cpl_unexpect),
        .cfg_err_ecrc(cfg_err_ecrc),
        .cfg_err_internal_cor(cfg_err_internal_cor),
        .cfg_err_internal_uncor(cfg_err_internal_uncor),
        .cfg_err_locked(cfg_err_locked),
        .cfg_err_malformed(cfg_err_malformed),
        .cfg_err_mc_blocked(cfg_err_mc_blocked),
        .cfg_err_norecovery(cfg_err_norecovery),
        .cfg_err_poisoned(cfg_err_poisoned),
        .cfg_err_posted(cfg_err_posted),
        .cfg_err_tlp_cpl_header(cfg_err_tlp_cpl_header),
        .cfg_err_ur(cfg_err_ur),
        .cfg_interrupt(cfg_interrupt),
        .cfg_interrupt_assert(cfg_interrupt_assert),
        .cfg_interrupt_di(cfg_interrupt_di),
        .cfg_interrupt_do(cfg_interrupt_do),
        .cfg_interrupt_mmenable(cfg_interrupt_mmenable),
        .cfg_interrupt_msienable(cfg_interrupt_msienable),
        .cfg_interrupt_msixenable(cfg_interrupt_msixenable),
        .cfg_interrupt_msixfm(cfg_interrupt_msixfm),
        .cfg_interrupt_rdy(cfg_interrupt_rdy),
        .cfg_interrupt_stat(cfg_interrupt_stat),
        .cfg_lcommand(cfg_lcommand),
        .cfg_lstatus(cfg_lstatus),
        .cfg_mgmt_byte_en_n(cfg_mgmt_byte_en_n),
        .cfg_mgmt_di(cfg_mgmt_di),
        .cfg_mgmt_do(cfg_mgmt_do),
        .cfg_mgmt_dwaddr(cfg_mgmt_dwaddr),
        .cfg_mgmt_rd_en(cfg_mgmt_rd_en),
        .cfg_mgmt_rd_wr_done(cfg_mgmt_rd_wr_done),
        .cfg_mgmt_wr_en(cfg_mgmt_wr_en),
        .cfg_mgmt_wr_readonly(cfg_mgmt_wr_readonly),
        .cfg_mgmt_wr_rw1c_as_rw(cfg_mgmt_wr_rw1c_as_rw),
        .cfg_msg_data(cfg_msg_data),
        .cfg_msg_received(cfg_msg_received),
        .cfg_msg_received_assert_int_a(cfg_msg_received_assert_int_a),
        .cfg_msg_received_assert_int_b(cfg_msg_received_assert_int_b),
        .cfg_msg_received_assert_int_c(cfg_msg_received_assert_int_c),
        .cfg_msg_received_assert_int_d(cfg_msg_received_assert_int_d),
        .cfg_msg_received_deassert_int_a(cfg_msg_received_deassert_int_a),
        .cfg_msg_received_deassert_int_b(cfg_msg_received_deassert_int_b),
        .cfg_msg_received_deassert_int_c(cfg_msg_received_deassert_int_c),
        .cfg_msg_received_deassert_int_d(cfg_msg_received_deassert_int_d),
        .cfg_msg_received_err_cor(cfg_msg_received_err_cor),
        .cfg_msg_received_err_fatal(cfg_msg_received_err_fatal),
        .cfg_msg_received_err_non_fatal(cfg_msg_received_err_non_fatal),
        .cfg_msg_received_pm_as_nak(cfg_msg_received_pm_as_nak),
        .cfg_msg_received_pm_pme(cfg_msg_received_pm_pme),
        .cfg_msg_received_pme_to_ack(cfg_msg_received_pme_to_ack),
        .cfg_msg_received_setslotpowerlimit(cfg_msg_received_setslotpowerlimit),
        .cfg_pcie_link_state(cfg_pcie_link_state),
        .cfg_pciecap_interrupt_msgnum(cfg_pciecap_interrupt_msgnum),
        .cfg_pm_force_state(cfg_pm_force_state),
        .cfg_pm_force_state_en(cfg_pm_force_state_en),
        .cfg_pm_halt_aspm_l0s(cfg_pm_halt_aspm_l0s),
        .cfg_pm_halt_aspm_l1(cfg_pm_halt_aspm_l1),
        .cfg_pm_turnoff_ok_n(cfg_turnoff_ok_w),
        .cfg_pm_wake(cfg_pm_wake),
        .cfg_pmcsr_pme_en(cfg_pmcsr_pme_en),
        .cfg_pmcsr_pme_status(cfg_pmcsr_pme_status),
        .cfg_pmcsr_powerstate(cfg_pmcsr_powerstate),
        .cfg_received_func_lvl_rst(cfg_received_func_lvl_rst),
        .cfg_root_control_pme_int_en(cfg_root_control_pme_int_en),
        .cfg_root_control_syserr_corr_err_en(cfg_root_control_syserr_corr_err_en),
        .cfg_root_control_syserr_fatal_err_en(cfg_root_control_syserr_fatal_err_en),
        .cfg_root_control_syserr_non_fatal_err_en(cfg_root_control_syserr_non_fatal_err_en),
        .cfg_slot_control_electromech_il_ctl_pulse(cfg_slot_control_electromech_il_ctl_pulse),
        .cfg_to_turnoff(cfg_to_turnoff),
        .cfg_trn_pending(cfg_trn_pending),
        .cfg_vc_tcvc_map(cfg_vc_tcvc_map),
        .dsc_detect(\rx_inst/rx_pipeline_inst/dsc_detect ),
        .fc_cpld(fc_cpld),
        .fc_cplh(fc_cplh),
        .fc_npd(fc_npd),
        .fc_nph(fc_nph),
        .fc_pd(fc_pd),
        .fc_ph(fc_ph),
        .fc_sel(fc_sel),
        .lnk_up_thrtl(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/lnk_up_thrtl ),
        .out(out),
        .pcie_block_i_0(pcie_7x_i_n_13),
        .pcie_block_i_1(pcie_7x_i_n_22),
        .pcie_block_i_2(pcie_7x_i_n_30),
        .pcie_block_i_3(trn_rd),
        .pcie_block_i_4(trn_rrem),
        .pcie_block_i_5({trn_tsrc_dsc,trn_tstr,trn_terrfwd,trn_tecrc_gen}),
        .pcie_drp_addr(pcie_drp_addr),
        .pcie_drp_clk(pcie_drp_clk),
        .pcie_drp_di(pcie_drp_di),
        .pcie_drp_do(pcie_drp_do),
        .pcie_drp_en(pcie_drp_en),
        .pcie_drp_rdy(pcie_drp_rdy),
        .pcie_drp_we(pcie_drp_we),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_rx0_chanisaligned(pipe_rx0_chanisaligned),
        .pipe_rx0_char_is_k(pipe_rx0_char_is_k),
        .pipe_rx0_data(pipe_rx0_data),
        .pipe_rx0_elec_idle(pipe_rx0_elec_idle),
        .pipe_rx0_phy_status(pipe_rx0_phy_status),
        .pipe_rx0_polarity(pipe_rx0_polarity),
        .pipe_rx0_status(pipe_rx0_status),
        .pipe_rx0_valid(pipe_rx0_valid),
        .pipe_tx0_char_is_k(pipe_tx0_char_is_k),
        .pipe_tx0_compliance(pipe_tx0_compliance),
        .pipe_tx0_data(pipe_tx0_data),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle),
        .pipe_tx0_powerdown(pipe_tx0_powerdown),
        .pipe_tx_deemph(pipe_tx_deemph),
        .pipe_tx_margin(pipe_tx_margin),
        .pipe_tx_rate(pipe_tx_rate),
        .pipe_tx_rcvr_det(pipe_tx_rcvr_det),
        .pipe_userclk1_in(pipe_userclk1_in),
        .pipe_userclk2_in(pipe_userclk2_in),
        .pl_directed_change_done(pl_directed_change_done),
        .pl_directed_link_auton(pl_directed_link_auton),
        .pl_directed_link_change(pl_directed_link_change),
        .pl_directed_link_speed(pl_directed_link_speed),
        .pl_directed_link_width(pl_directed_link_width),
        .pl_downstream_deemph_source(pl_downstream_deemph_source),
        .pl_initial_link_width(pl_initial_link_width),
        .pl_lane_reversal_mode(pl_lane_reversal_mode),
        .pl_link_gen2_cap(pl_link_gen2_cap),
        .pl_link_partner_gen2_supported(pl_link_partner_gen2_supported),
        .pl_link_upcfg_cap(pl_link_upcfg_cap),
        .pl_ltssm_state(pl_ltssm_state),
        .pl_phy_lnk_up(pl_phy_lnk_up),
        .pl_received_hot_rst(pl_received_hot_rst),
        .pl_rx_pm_state(pl_rx_pm_state),
        .pl_sel_lnk_rate(pl_sel_lnk_rate),
        .pl_sel_lnk_width(pl_sel_lnk_width),
        .pl_transmit_hot_rst(pl_transmit_hot_rst),
        .pl_tx_pm_state(pl_tx_pm_state),
        .pl_upstream_prefer_deemph(pl_upstream_prefer_deemph),
        .ppm_L1_thrtl(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_thrtl ),
        .ppm_L1_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/ppm_L1_trig ),
        .reg_dsc_detect(\rx_inst/rx_pipeline_inst/reg_dsc_detect ),
        .reg_tcfg_gnt(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/reg_tcfg_gnt ),
        .rsrc_rdy_filtered(\rx_inst/rx_pipeline_inst/rsrc_rdy_filtered ),
        .rx_np_ok(rx_np_ok),
        .rx_np_req(rx_np_req),
        .src_in(src_in),
        .sys_rst_n(sys_rst_n),
        .tbuf_av_min_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tbuf_av_min_trig ),
        .tcfg_req_trig(\tx_inst/thrtl_ctl_enabled.tx_thrl_ctl_inst/tcfg_req_trig ),
        .trn_in_packet(\rx_inst/rx_pipeline_inst/trn_in_packet ),
        .trn_in_packet_reg(pcie_7x_i_n_9),
        .trn_lnk_up(trn_lnk_up),
        .trn_rbar_hit(trn_rbar_hit),
        .trn_rdst_rdy(trn_rdst_rdy),
        .trn_recrc_err(trn_recrc_err),
        .trn_reof(trn_reof),
        .trn_rerrfwd(trn_rerrfwd),
        .trn_rsof(trn_rsof),
        .trn_rsrc_dsc(trn_rsrc_dsc),
        .trn_rsrc_dsc_d(\rx_inst/rx_pipeline_inst/trn_rsrc_dsc_d ),
        .trn_rsrc_dsc_prev0(\rx_inst/rx_pipeline_inst/trn_rsrc_dsc_prev0 ),
        .trn_tbuf_av(trn_tbuf_av),
        .trn_tcfg_gnt(trn_tcfg_gnt),
        .trn_tcfg_req(trn_tcfg_req),
        .trn_td(trn_td),
        .trn_tdst_rdy(trn_tdst_rdy),
        .trn_teof(trn_teof),
        .trn_trem(trn_trem),
        .trn_tsof(trn_tsof),
        .trn_tsrc_rdy(trn_tsrc_rdy),
        .tx_err_drop(tx_err_drop),
        .user_reset_int_reg(user_reset_int_reg));
endmodule

module pcie_7x_bridge_pipe_eq
   (rxeq_adapt_done,
    TXPRECURSOR,
    TXMAINCURSOR,
    TXPOSTCURSOR,
    rst_cpllreset,
    pipe_pclk_in);
  output rxeq_adapt_done;
  output [4:0]TXPRECURSOR;
  output [6:0]TXMAINCURSOR;
  output [4:0]TXPOSTCURSOR;
  input rst_cpllreset;
  input pipe_pclk_in;

  wire \FSM_onehot_fsm_rx[1]_i_1_n_0 ;
  wire \FSM_onehot_fsm_rx[1]_i_2_n_0 ;
  wire \FSM_onehot_fsm_rx[3]_i_1_n_0 ;
  wire \FSM_onehot_fsm_rx[4]_i_1_n_0 ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[1] ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[2] ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[3] ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[4] ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[5] ;
  wire \FSM_onehot_fsm_rx_reg_n_0_[6] ;
  wire \FSM_sequential_fsm_tx[1]_i_2_n_0 ;
  wire \FSM_sequential_fsm_tx[2]_i_2_n_0 ;
  wire \FSM_sequential_fsm_tx[2]_i_3_n_0 ;
  wire \FSM_sequential_fsm_tx[2]_i_4_n_0 ;
  wire [6:0]TXMAINCURSOR;
  wire [4:0]TXPOSTCURSOR;
  wire [4:0]TXPRECURSOR;
  wire [2:0]fsm_tx;
  wire [2:0]fsm_tx__0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg2;
  wire [6:6]in10;
  wire [11:0]in10__0;
  wire [12:12]in7;
  wire [15:2]p_0_out;
  wire pipe_pclk_in;
  wire rst_cpllreset;
  wire rxeq_adapt_done;
  wire rxeq_adapt_done_i_2_n_0;
  wire rxeq_adapt_done_reg_i_2_n_0;
  wire rxeq_adapt_done_reg_reg_n_0;
  wire [2:0]rxeq_cnt;
  wire \rxeq_cnt_reg_n_0_[0] ;
  wire \rxeq_cnt_reg_n_0_[1] ;
  wire \rxeq_cnt_reg_n_0_[2] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rxeq_control_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rxeq_control_reg2;
  wire [5:0]rxeq_fs;
  wire \rxeq_fs[5]_i_1_n_0 ;
  wire \rxeq_fs_reg_n_0_[0] ;
  wire \rxeq_fs_reg_n_0_[1] ;
  wire \rxeq_fs_reg_n_0_[2] ;
  wire \rxeq_fs_reg_n_0_[3] ;
  wire \rxeq_fs_reg_n_0_[4] ;
  wire \rxeq_fs_reg_n_0_[5] ;
  wire [5:0]rxeq_lf;
  wire \rxeq_lf[5]_i_1_n_0 ;
  wire \rxeq_lf_reg_n_0_[0] ;
  wire \rxeq_lf_reg_n_0_[1] ;
  wire \rxeq_lf_reg_n_0_[2] ;
  wire \rxeq_lf_reg_n_0_[3] ;
  wire \rxeq_lf_reg_n_0_[4] ;
  wire \rxeq_lf_reg_n_0_[5] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]rxeq_lffs_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]rxeq_lffs_reg2;
  wire rxeq_new_txcoeff_req;
  wire rxeq_new_txcoeff_req_0;
  wire \rxeq_preset[0]_i_1_n_0 ;
  wire \rxeq_preset[1]_i_1_n_0 ;
  wire \rxeq_preset[2]_i_1_n_0 ;
  wire \rxeq_preset[2]_i_2_n_0 ;
  wire \rxeq_preset[2]_i_3_n_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [2:0]rxeq_preset_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [2:0]rxeq_preset_reg2;
  wire \rxeq_preset_reg_n_0_[0] ;
  wire \rxeq_preset_reg_n_0_[1] ;
  wire \rxeq_preset_reg_n_0_[2] ;
  wire rxeq_preset_valid;
  wire rxeq_scan_i_n_0;
  wire rxeq_scan_i_n_1;
  wire rxeq_scan_i_n_2;
  wire rxeq_scan_i_n_3;
  wire rxeq_scan_i_n_4;
  wire [17:0]rxeq_txcoeff;
  wire \rxeq_txcoeff_reg_n_0_[0] ;
  wire \rxeq_txcoeff_reg_n_0_[1] ;
  wire \rxeq_txcoeff_reg_n_0_[2] ;
  wire \rxeq_txcoeff_reg_n_0_[3] ;
  wire \rxeq_txcoeff_reg_n_0_[4] ;
  wire \rxeq_txcoeff_reg_n_0_[5] ;
  wire [3:0]rxeq_txpreset;
  wire \rxeq_txpreset[3]_i_1_n_0 ;
  wire \rxeq_txpreset[3]_i_3_n_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]rxeq_txpreset_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]rxeq_txpreset_reg2;
  wire \rxeq_txpreset_reg_n_0_[0] ;
  wire \rxeq_txpreset_reg_n_0_[1] ;
  wire \rxeq_txpreset_reg_n_0_[2] ;
  wire \rxeq_txpreset_reg_n_0_[3] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_user_en_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_user_en_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_user_mode_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_user_mode_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [17:0]rxeq_user_txcoeff_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [17:0]rxeq_user_txcoeff_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]txeq_control_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]txeq_control_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]txeq_deemph_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]txeq_deemph_reg2;
  wire [17:0]txeq_preset;
  wire \txeq_preset[0]_i_1_n_0 ;
  wire \txeq_preset[13]_i_1_n_0 ;
  wire \txeq_preset[14]_i_1_n_0 ;
  wire \txeq_preset[15]_i_1_n_0 ;
  wire \txeq_preset[16]_i_1_n_0 ;
  wire \txeq_preset[16]_i_2_n_0 ;
  wire \txeq_preset[17]_i_1_n_0 ;
  wire \txeq_preset[17]_i_2_n_0 ;
  wire \txeq_preset[1]_i_1_n_0 ;
  wire \txeq_preset[7]_i_1_n_0 ;
  wire \txeq_preset[7]_i_2_n_0 ;
  wire txeq_preset_done;
  wire txeq_preset_done_i_1_n_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]txeq_preset_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]txeq_preset_reg2;
  wire txeq_txcoeff;
  wire \txeq_txcoeff[0]_i_1_n_0 ;
  wire \txeq_txcoeff[0]_i_2_n_0 ;
  wire \txeq_txcoeff[10]_i_1_n_0 ;
  wire \txeq_txcoeff[10]_i_2_n_0 ;
  wire \txeq_txcoeff[11]_i_1_n_0 ;
  wire \txeq_txcoeff[11]_i_2_n_0 ;
  wire \txeq_txcoeff[12]_i_1_n_0 ;
  wire \txeq_txcoeff[12]_i_2_n_0 ;
  wire \txeq_txcoeff[13]_i_1_n_0 ;
  wire \txeq_txcoeff[13]_i_2_n_0 ;
  wire \txeq_txcoeff[14]_i_1_n_0 ;
  wire \txeq_txcoeff[14]_i_2_n_0 ;
  wire \txeq_txcoeff[15]_i_1_n_0 ;
  wire \txeq_txcoeff[15]_i_2_n_0 ;
  wire \txeq_txcoeff[16]_i_1_n_0 ;
  wire \txeq_txcoeff[16]_i_2_n_0 ;
  wire \txeq_txcoeff[17]_i_1_n_0 ;
  wire \txeq_txcoeff[17]_i_2_n_0 ;
  wire \txeq_txcoeff[18]_i_2_n_0 ;
  wire \txeq_txcoeff[18]_i_3_n_0 ;
  wire \txeq_txcoeff[1]_i_1_n_0 ;
  wire \txeq_txcoeff[1]_i_2_n_0 ;
  wire \txeq_txcoeff[2]_i_1_n_0 ;
  wire \txeq_txcoeff[2]_i_2_n_0 ;
  wire \txeq_txcoeff[3]_i_1_n_0 ;
  wire \txeq_txcoeff[3]_i_2_n_0 ;
  wire \txeq_txcoeff[4]_i_1_n_0 ;
  wire \txeq_txcoeff[4]_i_2_n_0 ;
  wire \txeq_txcoeff[5]_i_1_n_0 ;
  wire \txeq_txcoeff[5]_i_2_n_0 ;
  wire \txeq_txcoeff[6]_i_1_n_0 ;
  wire \txeq_txcoeff[6]_i_2_n_0 ;
  wire \txeq_txcoeff[7]_i_1_n_0 ;
  wire \txeq_txcoeff[7]_i_2_n_0 ;
  wire \txeq_txcoeff[8]_i_1_n_0 ;
  wire \txeq_txcoeff[8]_i_2_n_0 ;
  wire \txeq_txcoeff[9]_i_1_n_0 ;
  wire \txeq_txcoeff[9]_i_2_n_0 ;
  wire [1:0]txeq_txcoeff_cnt;
  wire \txeq_txcoeff_cnt_reg_n_0_[0] ;
  wire \txeq_txcoeff_cnt_reg_n_0_[1] ;
  wire \txeq_txcoeff_reg_n_0_[0] ;
  wire \txeq_txcoeff_reg_n_0_[10] ;
  wire \txeq_txcoeff_reg_n_0_[11] ;
  wire \txeq_txcoeff_reg_n_0_[12] ;
  wire \txeq_txcoeff_reg_n_0_[13] ;
  wire \txeq_txcoeff_reg_n_0_[14] ;
  wire \txeq_txcoeff_reg_n_0_[15] ;
  wire \txeq_txcoeff_reg_n_0_[16] ;
  wire \txeq_txcoeff_reg_n_0_[17] ;
  wire \txeq_txcoeff_reg_n_0_[1] ;
  wire \txeq_txcoeff_reg_n_0_[2] ;
  wire \txeq_txcoeff_reg_n_0_[3] ;
  wire \txeq_txcoeff_reg_n_0_[4] ;
  wire \txeq_txcoeff_reg_n_0_[6] ;
  wire \txeq_txcoeff_reg_n_0_[7] ;
  wire \txeq_txcoeff_reg_n_0_[8] ;
  wire \txeq_txcoeff_reg_n_0_[9] ;

  LUT5 #(
    .INIT(32'hABABABAA)) 
    \FSM_onehot_fsm_rx[1]_i_1 
       (.I0(\FSM_onehot_fsm_rx[1]_i_2_n_0 ),
        .I1(rxeq_control_reg2[0]),
        .I2(rxeq_control_reg2[1]),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .O(\FSM_onehot_fsm_rx[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h0000000000000001)) 
    \FSM_onehot_fsm_rx[1]_i_2 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I5(\FSM_onehot_fsm_rx_reg_n_0_[5] ),
        .O(\FSM_onehot_fsm_rx[1]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFF8FF88888888)) 
    \FSM_onehot_fsm_rx[3]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_control_reg2[1]),
        .I2(\rxeq_cnt_reg_n_0_[0] ),
        .I3(\rxeq_cnt_reg_n_0_[1] ),
        .I4(\rxeq_cnt_reg_n_0_[2] ),
        .I5(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .O(\FSM_onehot_fsm_rx[3]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair32" *) 
  LUT5 #(
    .INIT(32'h2ABA2AAA)) 
    \FSM_onehot_fsm_rx[4]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(\rxeq_cnt_reg_n_0_[0] ),
        .I2(\rxeq_cnt_reg_n_0_[1] ),
        .I3(\rxeq_cnt_reg_n_0_[2] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .O(\FSM_onehot_fsm_rx[4]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDSE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm_rx[1]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_scan_i_n_4),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm_rx[3]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm_rx[4]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_scan_i_n_3),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[5] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RXEQ_PRESET:0000100,FSM_RXEQ_TXCOEFF:0001000,FSM_RXEQ_LF:0010000,FSM_RXEQ_NEW_TXCOEFF_REQ:0100000,FSM_RXEQ_DONE:1000000,FSM_RXEQ_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_rx_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_scan_i_n_2),
        .Q(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'hC04FC043C04FF04F)) 
    \FSM_sequential_fsm_tx[0]_i_1 
       (.I0(\FSM_sequential_fsm_tx[1]_i_2_n_0 ),
        .I1(fsm_tx[0]),
        .I2(fsm_tx[1]),
        .I3(fsm_tx[2]),
        .I4(txeq_control_reg2[1]),
        .I5(txeq_control_reg2[0]),
        .O(fsm_tx__0[0]));
  LUT6 #(
    .INIT(64'h3F703F7C3F7C0F70)) 
    \FSM_sequential_fsm_tx[1]_i_1 
       (.I0(\FSM_sequential_fsm_tx[1]_i_2_n_0 ),
        .I1(fsm_tx[0]),
        .I2(fsm_tx[1]),
        .I3(fsm_tx[2]),
        .I4(txeq_control_reg2[1]),
        .I5(txeq_control_reg2[0]),
        .O(fsm_tx__0[1]));
  (* SOFT_HLUTNM = "soft_lutpair40" *) 
  LUT2 #(
    .INIT(4'h2)) 
    \FSM_sequential_fsm_tx[1]_i_2 
       (.I0(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .O(\FSM_sequential_fsm_tx[1]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hA8A8A8A8A8AAA8A8)) 
    \FSM_sequential_fsm_tx[2]_i_1 
       (.I0(\FSM_sequential_fsm_tx[2]_i_2_n_0 ),
        .I1(\FSM_sequential_fsm_tx[2]_i_3_n_0 ),
        .I2(fsm_tx[2]),
        .I3(\FSM_sequential_fsm_tx[2]_i_4_n_0 ),
        .I4(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I5(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .O(fsm_tx__0[2]));
  LUT5 #(
    .INIT(32'h7777FFF7)) 
    \FSM_sequential_fsm_tx[2]_i_2 
       (.I0(fsm_tx[1]),
        .I1(fsm_tx[2]),
        .I2(txeq_control_reg2[1]),
        .I3(txeq_control_reg2[0]),
        .I4(fsm_tx[0]),
        .O(\FSM_sequential_fsm_tx[2]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h0F800080)) 
    \FSM_sequential_fsm_tx[2]_i_3 
       (.I0(txeq_control_reg2[1]),
        .I1(txeq_control_reg2[0]),
        .I2(fsm_tx[0]),
        .I3(fsm_tx[1]),
        .I4(txeq_preset_done),
        .O(\FSM_sequential_fsm_tx[2]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair30" *) 
  LUT2 #(
    .INIT(4'h7)) 
    \FSM_sequential_fsm_tx[2]_i_4 
       (.I0(fsm_tx[0]),
        .I1(fsm_tx[1]),
        .O(\FSM_sequential_fsm_tx[2]_i_4_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_TXEQ_QUERY:101,FSM_TXEQ_PRESET:010,FSM_TXEQ_TXCOEFF:011,FSM_TXEQ_REMAP:100,FSM_TXEQ_DONE:110,FSM_TXEQ_IDLE:001,iSTATE:000" *) 
  FDSE #(
    .INIT(1'b0)) 
    \FSM_sequential_fsm_tx_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fsm_tx__0[0]),
        .Q(fsm_tx[0]),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_TXEQ_QUERY:101,FSM_TXEQ_PRESET:010,FSM_TXEQ_TXCOEFF:011,FSM_TXEQ_REMAP:100,FSM_TXEQ_DONE:110,FSM_TXEQ_IDLE:001,iSTATE:000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_sequential_fsm_tx_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fsm_tx__0[1]),
        .Q(fsm_tx[1]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_TXEQ_QUERY:101,FSM_TXEQ_PRESET:010,FSM_TXEQ_TXCOEFF:011,FSM_TXEQ_REMAP:100,FSM_TXEQ_DONE:110,FSM_TXEQ_IDLE:001,iSTATE:000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_sequential_fsm_tx_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fsm_tx__0[2]),
        .Q(fsm_tx[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(gen3_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gen3_reg1),
        .Q(gen3_reg2),
        .R(rst_cpllreset));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_22 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[17] ),
        .O(TXPOSTCURSOR[4]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_23 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[16] ),
        .O(TXPOSTCURSOR[3]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_24 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[15] ),
        .O(TXPOSTCURSOR[2]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_25 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[14] ),
        .O(TXPOSTCURSOR[1]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_26 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[13] ),
        .O(TXPOSTCURSOR[0]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_27 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[4] ),
        .O(TXPRECURSOR[4]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_28 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[3] ),
        .O(TXPRECURSOR[3]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_29 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[2] ),
        .O(TXPRECURSOR[2]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_30 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[1] ),
        .O(TXPRECURSOR[1]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_31 
       (.I0(\txeq_txcoeff_reg_n_0_[0] ),
        .I1(gen3_reg2),
        .O(TXPRECURSOR[0]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_32 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[12] ),
        .O(TXMAINCURSOR[6]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_33 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[11] ),
        .O(TXMAINCURSOR[5]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_34 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[10] ),
        .O(TXMAINCURSOR[4]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_35 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[9] ),
        .O(TXMAINCURSOR[3]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_36 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[8] ),
        .O(TXMAINCURSOR[2]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_37 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[7] ),
        .O(TXMAINCURSOR[1]));
  LUT2 #(
    .INIT(4'h8)) 
    \gtp_channel.gtpe2_channel_i_i_38 
       (.I0(gen3_reg2),
        .I1(\txeq_txcoeff_reg_n_0_[6] ),
        .O(TXMAINCURSOR[0]));
  LUT6 #(
    .INIT(64'hFFFFFFFEFFFFFFFF)) 
    rxeq_adapt_done_i_2
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[5] ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I5(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .O(rxeq_adapt_done_i_2_n_0));
  FDRE #(
    .INIT(1'b0)) 
    rxeq_adapt_done_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_scan_i_n_1),
        .Q(rxeq_adapt_done),
        .R(rst_cpllreset));
  LUT3 #(
    .INIT(8'h08)) 
    rxeq_adapt_done_reg_i_2
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_control_reg2[0]),
        .I2(rxeq_control_reg2[1]),
        .O(rxeq_adapt_done_reg_i_2_n_0));
  FDRE #(
    .INIT(1'b0)) 
    rxeq_adapt_done_reg_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_scan_i_n_0),
        .Q(rxeq_adapt_done_reg_reg_n_0),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'h8888FFF8)) 
    \rxeq_cnt[0]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_control_reg2[1]),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I4(\rxeq_cnt_reg_n_0_[0] ),
        .O(rxeq_cnt[0]));
  (* SOFT_HLUTNM = "soft_lutpair33" *) 
  LUT4 #(
    .INIT(16'h6660)) 
    \rxeq_cnt[1]_i_1 
       (.I0(\rxeq_cnt_reg_n_0_[1] ),
        .I1(\rxeq_cnt_reg_n_0_[0] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .O(rxeq_cnt[1]));
  (* SOFT_HLUTNM = "soft_lutpair32" *) 
  LUT5 #(
    .INIT(32'h0EEEE000)) 
    \rxeq_cnt[2]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\rxeq_cnt_reg_n_0_[0] ),
        .I3(\rxeq_cnt_reg_n_0_[1] ),
        .I4(\rxeq_cnt_reg_n_0_[2] ),
        .O(rxeq_cnt[2]));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_cnt[0]),
        .Q(\rxeq_cnt_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_cnt[1]),
        .Q(\rxeq_cnt_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_cnt[2]),
        .Q(\rxeq_cnt_reg_n_0_[2] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_control_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_control_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_control_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_control_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_control_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_control_reg1[0]),
        .Q(rxeq_control_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_control_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_control_reg1[1]),
        .Q(rxeq_control_reg2[1]),
        .R(rst_cpllreset));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[0]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[0]),
        .O(rxeq_fs[0]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[1]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[1]),
        .O(rxeq_fs[1]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[2]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[2]),
        .O(rxeq_fs[2]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[3]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[3]),
        .O(rxeq_fs[3]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[4]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[4]),
        .O(rxeq_fs[4]));
  LUT3 #(
    .INIT(8'hF8)) 
    \rxeq_fs[5]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_control_reg2[1]),
        .I2(\FSM_onehot_fsm_rx[1]_i_2_n_0 ),
        .O(\rxeq_fs[5]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_fs[5]_i_2 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(rxeq_lffs_reg2[5]),
        .O(rxeq_fs[5]));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[0]),
        .Q(\rxeq_fs_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[1]),
        .Q(\rxeq_fs_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[2]),
        .Q(\rxeq_fs_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[3]),
        .Q(\rxeq_fs_reg_n_0_[3] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[4] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[4]),
        .Q(\rxeq_fs_reg_n_0_[4] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_fs_reg[5] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_fs[5]_i_1_n_0 ),
        .D(rxeq_fs[5]),
        .Q(\rxeq_fs_reg_n_0_[5] ),
        .R(rst_cpllreset));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[0]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[0]),
        .O(rxeq_lf[0]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[1]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[1]),
        .O(rxeq_lf[1]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[2]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[2]),
        .O(rxeq_lf[2]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[3]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[3]),
        .O(rxeq_lf[3]));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[4]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[4]),
        .O(rxeq_lf[4]));
  LUT5 #(
    .INIT(32'hEAAAAAAA)) 
    \rxeq_lf[5]_i_1 
       (.I0(\FSM_onehot_fsm_rx[1]_i_2_n_0 ),
        .I1(\rxeq_cnt_reg_n_0_[2] ),
        .I2(\rxeq_cnt_reg_n_0_[1] ),
        .I3(\rxeq_cnt_reg_n_0_[0] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .O(\rxeq_lf[5]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h8)) 
    \rxeq_lf[5]_i_2 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I1(rxeq_lffs_reg2[5]),
        .O(rxeq_lf[5]));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[0]),
        .Q(\rxeq_lf_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[1]),
        .Q(\rxeq_lf_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[2]),
        .Q(\rxeq_lf_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[3]),
        .Q(\rxeq_lf_reg_n_0_[3] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[4] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[4]),
        .Q(\rxeq_lf_reg_n_0_[4] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_lf_reg[5] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_lf[5]_i_1_n_0 ),
        .D(rxeq_lf[5]),
        .Q(\rxeq_lf_reg_n_0_[5] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_lffs_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[0]),
        .Q(rxeq_lffs_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[1]),
        .Q(rxeq_lffs_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[2]),
        .Q(rxeq_lffs_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[3]),
        .Q(rxeq_lffs_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[4]),
        .Q(rxeq_lffs_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_lffs_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_lffs_reg1[5]),
        .Q(rxeq_lffs_reg2[5]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    rxeq_new_txcoeff_req_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_new_txcoeff_req_0),
        .Q(rxeq_new_txcoeff_req),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'hA8FFA800)) 
    \rxeq_preset[0]_i_1 
       (.I0(rxeq_preset_reg2[0]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I3(\rxeq_preset[2]_i_2_n_0 ),
        .I4(\rxeq_preset_reg_n_0_[0] ),
        .O(\rxeq_preset[0]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hA8FFA800)) 
    \rxeq_preset[1]_i_1 
       (.I0(rxeq_preset_reg2[1]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I3(\rxeq_preset[2]_i_2_n_0 ),
        .I4(\rxeq_preset_reg_n_0_[1] ),
        .O(\rxeq_preset[1]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hA8FFA800)) 
    \rxeq_preset[2]_i_1 
       (.I0(rxeq_preset_reg2[2]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I3(\rxeq_preset[2]_i_2_n_0 ),
        .I4(\rxeq_preset_reg_n_0_[2] ),
        .O(\rxeq_preset[2]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFF0002)) 
    \rxeq_preset[2]_i_2 
       (.I0(\rxeq_preset[2]_i_3_n_0 ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[5] ),
        .I4(rxeq_adapt_done_reg_i_2_n_0),
        .I5(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .O(\rxeq_preset[2]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair33" *) 
  LUT2 #(
    .INIT(4'h1)) 
    \rxeq_preset[2]_i_3 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .O(\rxeq_preset[2]_i_3_n_0 ));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_preset_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_preset_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_preset_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_preset_reg1[0]),
        .Q(rxeq_preset_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_preset_reg1[1]),
        .Q(rxeq_preset_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_preset_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_preset_reg1[2]),
        .Q(rxeq_preset_reg2[2]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_preset_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rxeq_preset[0]_i_1_n_0 ),
        .Q(\rxeq_preset_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_preset_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rxeq_preset[1]_i_1_n_0 ),
        .Q(\rxeq_preset_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_preset_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rxeq_preset[2]_i_1_n_0 ),
        .Q(\rxeq_preset_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    rxeq_preset_valid_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .Q(rxeq_preset_valid),
        .R(rst_cpllreset));
  pcie_7x_bridge_rxeq_scan rxeq_scan_i
       (.D({rxeq_scan_i_n_2,rxeq_scan_i_n_3,rxeq_scan_i_n_4}),
        .\FSM_onehot_fsm_rx_reg[5] ({\rxeq_cnt_reg_n_0_[2] ,\rxeq_cnt_reg_n_0_[1] ,\rxeq_cnt_reg_n_0_[0] }),
        .Q({\FSM_onehot_fsm_rx_reg_n_0_[6] ,\FSM_onehot_fsm_rx_reg_n_0_[5] ,\FSM_onehot_fsm_rx_reg_n_0_[4] ,\FSM_onehot_fsm_rx_reg_n_0_[2] ,\FSM_onehot_fsm_rx_reg_n_0_[1] }),
        .adapt_done_reg_0(rxeq_scan_i_n_0),
        .\fs_reg1_reg[5]_0 ({\rxeq_fs_reg_n_0_[5] ,\rxeq_fs_reg_n_0_[4] ,\rxeq_fs_reg_n_0_[3] ,\rxeq_fs_reg_n_0_[2] ,\rxeq_fs_reg_n_0_[1] ,\rxeq_fs_reg_n_0_[0] }),
        .\lf_reg1_reg[5]_0 ({\rxeq_lf_reg_n_0_[5] ,\rxeq_lf_reg_n_0_[4] ,\rxeq_lf_reg_n_0_[3] ,\rxeq_lf_reg_n_0_[2] ,\rxeq_lf_reg_n_0_[1] ,\rxeq_lf_reg_n_0_[0] }),
        .new_txcoeff_done_reg_0(rxeq_scan_i_n_1),
        .out(rxeq_control_reg2),
        .pipe_pclk_in(pipe_pclk_in),
        .\preset_reg1_reg[2]_0 ({\rxeq_preset_reg_n_0_[2] ,\rxeq_preset_reg_n_0_[1] ,\rxeq_preset_reg_n_0_[0] }),
        .rst_cpllreset(rst_cpllreset),
        .rxeq_adapt_done(rxeq_adapt_done),
        .rxeq_adapt_done_reg(rxeq_adapt_done_i_2_n_0),
        .rxeq_adapt_done_reg_reg(\FSM_onehot_fsm_rx[1]_i_2_n_0 ),
        .rxeq_adapt_done_reg_reg_0(rxeq_adapt_done_reg_i_2_n_0),
        .rxeq_adapt_done_reg_reg_1(rxeq_adapt_done_reg_reg_n_0),
        .rxeq_new_txcoeff_req(rxeq_new_txcoeff_req),
        .rxeq_new_txcoeff_req_0(rxeq_new_txcoeff_req_0),
        .rxeq_preset_valid(rxeq_preset_valid),
        .\txcoeff_reg1_reg[17]_0 ({in10__0,\rxeq_txcoeff_reg_n_0_[5] ,\rxeq_txcoeff_reg_n_0_[4] ,\rxeq_txcoeff_reg_n_0_[3] ,\rxeq_txcoeff_reg_n_0_[2] ,\rxeq_txcoeff_reg_n_0_[1] ,\rxeq_txcoeff_reg_n_0_[0] }),
        .\txpreset_reg1_reg[3]_0 ({\rxeq_txpreset_reg_n_0_[3] ,\rxeq_txpreset_reg_n_0_[2] ,\rxeq_txpreset_reg_n_0_[1] ,\rxeq_txpreset_reg_n_0_[0] }));
  (* SOFT_HLUTNM = "soft_lutpair34" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[0]_i_1 
       (.I0(in10__0[0]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[0]));
  (* SOFT_HLUTNM = "soft_lutpair39" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[10]_i_1 
       (.I0(in10__0[10]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[10]));
  (* SOFT_HLUTNM = "soft_lutpair39" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[11]_i_1 
       (.I0(in10__0[11]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[11]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[12]_i_1 
       (.I0(txeq_deemph_reg2[0]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[12]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[13]_i_1 
       (.I0(txeq_deemph_reg2[1]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[13]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[14]_i_1 
       (.I0(txeq_deemph_reg2[2]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[14]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[15]_i_1 
       (.I0(txeq_deemph_reg2[3]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[15]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[16]_i_1 
       (.I0(txeq_deemph_reg2[4]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[16]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[17]_i_1 
       (.I0(txeq_deemph_reg2[5]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[17]));
  (* SOFT_HLUTNM = "soft_lutpair34" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[1]_i_1 
       (.I0(in10__0[1]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[1]));
  (* SOFT_HLUTNM = "soft_lutpair35" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[2]_i_1 
       (.I0(in10__0[2]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[2]));
  (* SOFT_HLUTNM = "soft_lutpair35" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[3]_i_1 
       (.I0(in10__0[3]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[3]));
  (* SOFT_HLUTNM = "soft_lutpair36" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[4]_i_1 
       (.I0(in10__0[4]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[4]));
  (* SOFT_HLUTNM = "soft_lutpair36" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[5]_i_1 
       (.I0(in10__0[5]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[5]));
  (* SOFT_HLUTNM = "soft_lutpair37" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[6]_i_1 
       (.I0(in10__0[6]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[6]));
  (* SOFT_HLUTNM = "soft_lutpair37" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[7]_i_1 
       (.I0(in10__0[7]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[7]));
  (* SOFT_HLUTNM = "soft_lutpair38" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[8]_i_1 
       (.I0(in10__0[8]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[8]));
  (* SOFT_HLUTNM = "soft_lutpair38" *) 
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txcoeff[9]_i_1 
       (.I0(in10__0[9]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txcoeff[9]));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[0]),
        .Q(\rxeq_txcoeff_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[10] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[10]),
        .Q(in10__0[4]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[11] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[11]),
        .Q(in10__0[5]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[12] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[12]),
        .Q(in10__0[6]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[13] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[13]),
        .Q(in10__0[7]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[14] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[14]),
        .Q(in10__0[8]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[15] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[15]),
        .Q(in10__0[9]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[16] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[16]),
        .Q(in10__0[10]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[17] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[17]),
        .Q(in10__0[11]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[1]),
        .Q(\rxeq_txcoeff_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[2]),
        .Q(\rxeq_txcoeff_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[3]),
        .Q(\rxeq_txcoeff_reg_n_0_[3] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[4] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[4]),
        .Q(\rxeq_txcoeff_reg_n_0_[4] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[5] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[5]),
        .Q(\rxeq_txcoeff_reg_n_0_[5] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[6] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[6]),
        .Q(in10__0[0]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[7] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[7]),
        .Q(in10__0[1]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[8] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[8]),
        .Q(in10__0[2]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txcoeff_reg[9] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txcoeff[9]),
        .Q(in10__0[3]),
        .R(rst_cpllreset));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txpreset[0]_i_1 
       (.I0(rxeq_txpreset_reg2[0]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txpreset[0]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txpreset[1]_i_1 
       (.I0(rxeq_txpreset_reg2[1]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txpreset[1]));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txpreset[2]_i_1 
       (.I0(rxeq_txpreset_reg2[2]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txpreset[2]));
  LUT5 #(
    .INIT(32'hFFFFF044)) 
    \rxeq_txpreset[3]_i_1 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[6] ),
        .I1(\rxeq_txpreset[3]_i_3_n_0 ),
        .I2(rxeq_control_reg2[1]),
        .I3(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .I4(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .O(\rxeq_txpreset[3]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'hA8)) 
    \rxeq_txpreset[3]_i_2 
       (.I0(rxeq_txpreset_reg2[3]),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[3] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[1] ),
        .O(rxeq_txpreset[3]));
  LUT3 #(
    .INIT(8'h01)) 
    \rxeq_txpreset[3]_i_3 
       (.I0(\FSM_onehot_fsm_rx_reg_n_0_[2] ),
        .I1(\FSM_onehot_fsm_rx_reg_n_0_[4] ),
        .I2(\FSM_onehot_fsm_rx_reg_n_0_[5] ),
        .O(\rxeq_txpreset[3]_i_3_n_0 ));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_txpreset_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_txpreset_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_txpreset_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_txpreset_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_txpreset_reg1[0]),
        .Q(rxeq_txpreset_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_txpreset_reg1[1]),
        .Q(rxeq_txpreset_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_txpreset_reg1[2]),
        .Q(rxeq_txpreset_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_txpreset_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_txpreset_reg1[3]),
        .Q(rxeq_txpreset_reg2[3]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txpreset_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txpreset[0]),
        .Q(\rxeq_txpreset_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txpreset_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txpreset[1]),
        .Q(\rxeq_txpreset_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txpreset_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txpreset[2]),
        .Q(\rxeq_txpreset_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxeq_txpreset_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\rxeq_txpreset[3]_i_1_n_0 ),
        .D(rxeq_txpreset[3]),
        .Q(\rxeq_txpreset_reg_n_0_[3] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_user_en_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_en_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_user_en_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_en_reg1),
        .Q(rxeq_user_en_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_user_mode_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_mode_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_user_mode_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_mode_reg1),
        .Q(rxeq_user_mode_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[10]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[11]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[12]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[13]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[14]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[15]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[16] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[16]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[17]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[6]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[7]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[8]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg1_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxeq_user_txcoeff_reg1[9]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[0]),
        .Q(rxeq_user_txcoeff_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[10]),
        .Q(rxeq_user_txcoeff_reg2[10]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[11]),
        .Q(rxeq_user_txcoeff_reg2[11]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[12]),
        .Q(rxeq_user_txcoeff_reg2[12]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[13]),
        .Q(rxeq_user_txcoeff_reg2[13]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[14]),
        .Q(rxeq_user_txcoeff_reg2[14]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[15]),
        .Q(rxeq_user_txcoeff_reg2[15]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[16] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[16]),
        .Q(rxeq_user_txcoeff_reg2[16]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[17]),
        .Q(rxeq_user_txcoeff_reg2[17]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[1]),
        .Q(rxeq_user_txcoeff_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[2]),
        .Q(rxeq_user_txcoeff_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[3]),
        .Q(rxeq_user_txcoeff_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[4]),
        .Q(rxeq_user_txcoeff_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[5]),
        .Q(rxeq_user_txcoeff_reg2[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[6]),
        .Q(rxeq_user_txcoeff_reg2[6]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[7]),
        .Q(rxeq_user_txcoeff_reg2[7]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[8]),
        .Q(rxeq_user_txcoeff_reg2[8]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rxeq_user_txcoeff_reg2_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_user_txcoeff_reg1[9]),
        .Q(rxeq_user_txcoeff_reg2[9]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_control_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_control_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_control_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_control_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_control_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_control_reg1[0]),
        .Q(txeq_control_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_control_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_control_reg1[1]),
        .Q(txeq_control_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \txeq_deemph_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[0]),
        .S(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_deemph_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \txeq_deemph_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[0]),
        .Q(txeq_deemph_reg2[0]),
        .S(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[1]),
        .Q(txeq_deemph_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[2]),
        .Q(txeq_deemph_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[3]),
        .Q(txeq_deemph_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[4]),
        .Q(txeq_deemph_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_deemph_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_deemph_reg1[5]),
        .Q(txeq_deemph_reg2[5]),
        .R(rst_cpllreset));
  LUT3 #(
    .INIT(8'h08)) 
    \txeq_preset[0]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[1]),
        .O(\txeq_preset[0]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hBAABAAEF)) 
    \txeq_preset[10]_i_1 
       (.I0(rst_cpllreset),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[1]),
        .I3(txeq_preset_reg2[0]),
        .I4(txeq_preset_reg2[2]),
        .O(p_0_out[10]));
  LUT5 #(
    .INIT(32'hFF18FF11)) 
    \txeq_preset[11]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[2]),
        .I2(txeq_preset_reg2[3]),
        .I3(rst_cpllreset),
        .I4(txeq_preset_reg2[1]),
        .O(p_0_out[11]));
  LUT5 #(
    .INIT(32'h0000133A)) 
    \txeq_preset[12]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[1]),
        .I3(txeq_preset_reg2[2]),
        .I4(rst_cpllreset),
        .O(p_0_out[12]));
  LUT3 #(
    .INIT(8'h42)) 
    \txeq_preset[13]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[1]),
        .I2(txeq_preset_reg2[3]),
        .O(\txeq_preset[13]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'h24)) 
    \txeq_preset[14]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[1]),
        .O(\txeq_preset[14]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hAABA)) 
    \txeq_preset[15]_i_1 
       (.I0(rst_cpllreset),
        .I1(fsm_tx[0]),
        .I2(fsm_tx[1]),
        .I3(fsm_tx[2]),
        .O(\txeq_preset[15]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hF0F1)) 
    \txeq_preset[15]_i_2 
       (.I0(txeq_preset_reg2[2]),
        .I1(txeq_preset_reg2[1]),
        .I2(rst_cpllreset),
        .I3(txeq_preset_reg2[3]),
        .O(p_0_out[15]));
  LUT5 #(
    .INIT(32'hFFFF0400)) 
    \txeq_preset[16]_i_1 
       (.I0(fsm_tx[2]),
        .I1(fsm_tx[1]),
        .I2(fsm_tx[0]),
        .I3(txeq_preset_reg2[2]),
        .I4(rst_cpllreset),
        .O(\txeq_preset[16]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h6)) 
    \txeq_preset[16]_i_2 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .O(\txeq_preset[16]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hFAFAFAFAFAFCFAFA)) 
    \txeq_preset[17]_i_1 
       (.I0(txeq_preset[17]),
        .I1(\txeq_preset[17]_i_2_n_0 ),
        .I2(rst_cpllreset),
        .I3(fsm_tx[0]),
        .I4(fsm_tx[1]),
        .I5(fsm_tx[2]),
        .O(\txeq_preset[17]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'h2051)) 
    \txeq_preset[17]_i_2 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[1]),
        .I3(txeq_preset_reg2[2]),
        .O(\txeq_preset[17]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h00000140)) 
    \txeq_preset[1]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[1]),
        .I2(txeq_preset_reg2[2]),
        .I3(txeq_preset_reg2[3]),
        .I4(rst_cpllreset),
        .O(\txeq_preset[1]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'h4440)) 
    \txeq_preset[2]_i_1 
       (.I0(rst_cpllreset),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[2]),
        .I3(txeq_preset_reg2[0]),
        .O(p_0_out[2]));
  LUT5 #(
    .INIT(32'h00003424)) 
    \txeq_preset[3]_i_1 
       (.I0(txeq_preset_reg2[1]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[2]),
        .I3(txeq_preset_reg2[0]),
        .I4(rst_cpllreset),
        .O(p_0_out[3]));
  LUT6 #(
    .INIT(64'h0000AAAA3C00AAAA)) 
    \txeq_preset[7]_i_1 
       (.I0(txeq_preset[7]),
        .I1(txeq_preset_reg2[0]),
        .I2(txeq_preset_reg2[2]),
        .I3(\txeq_preset[7]_i_2_n_0 ),
        .I4(\txeq_preset[15]_i_1_n_0 ),
        .I5(rst_cpllreset),
        .O(\txeq_preset[7]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \txeq_preset[7]_i_2 
       (.I0(txeq_preset_reg2[1]),
        .I1(txeq_preset_reg2[3]),
        .O(\txeq_preset[7]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hFFFF120F)) 
    \txeq_preset[8]_i_1 
       (.I0(txeq_preset_reg2[0]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[2]),
        .I3(txeq_preset_reg2[1]),
        .I4(rst_cpllreset),
        .O(p_0_out[8]));
  LUT5 #(
    .INIT(32'hFFFF300D)) 
    \txeq_preset[9]_i_1 
       (.I0(txeq_preset_reg2[1]),
        .I1(txeq_preset_reg2[3]),
        .I2(txeq_preset_reg2[2]),
        .I3(txeq_preset_reg2[0]),
        .I4(rst_cpllreset),
        .O(p_0_out[9]));
  (* SOFT_HLUTNM = "soft_lutpair31" *) 
  LUT3 #(
    .INIT(8'h04)) 
    txeq_preset_done_i_1
       (.I0(fsm_tx[2]),
        .I1(fsm_tx[1]),
        .I2(fsm_tx[0]),
        .O(txeq_preset_done_i_1_n_0));
  FDRE #(
    .INIT(1'b0)) 
    txeq_preset_done_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_preset_done_i_1_n_0),
        .Q(txeq_preset_done),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_preset_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_preset_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_preset_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(txeq_preset_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_preset_reg1[0]),
        .Q(txeq_preset_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_preset_reg1[1]),
        .Q(txeq_preset_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_preset_reg1[2]),
        .Q(txeq_preset_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txeq_preset_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_preset_reg1[3]),
        .Q(txeq_preset_reg2[3]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[0] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(\txeq_preset[0]_i_1_n_0 ),
        .Q(txeq_preset[0]),
        .R(\txeq_preset[16]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[10] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[10]),
        .Q(txeq_preset[10]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[11] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[11]),
        .Q(txeq_preset[11]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[12] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[12]),
        .Q(txeq_preset[12]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[13] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(\txeq_preset[13]_i_1_n_0 ),
        .Q(txeq_preset[13]),
        .R(\txeq_preset[16]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[14] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(\txeq_preset[14]_i_1_n_0 ),
        .Q(txeq_preset[14]),
        .R(\txeq_preset[16]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[15] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[15]),
        .Q(txeq_preset[15]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[16] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(\txeq_preset[16]_i_2_n_0 ),
        .Q(txeq_preset[16]),
        .R(\txeq_preset[16]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txeq_preset[17]_i_1_n_0 ),
        .Q(txeq_preset[17]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(\txeq_preset[1]_i_1_n_0 ),
        .Q(txeq_preset[1]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[2]),
        .Q(txeq_preset[2]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[3]),
        .Q(txeq_preset[3]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txeq_preset[7]_i_1_n_0 ),
        .Q(txeq_preset[7]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[8] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[8]),
        .Q(txeq_preset[8]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_preset_reg[9] 
       (.C(pipe_pclk_in),
        .CE(\txeq_preset[15]_i_1_n_0 ),
        .D(p_0_out[9]),
        .Q(txeq_preset[9]),
        .R(1'b0));
  (* SOFT_HLUTNM = "soft_lutpair30" *) 
  LUT5 #(
    .INIT(32'h45404040)) 
    \txeq_txcoeff[0]_i_1 
       (.I0(fsm_tx[2]),
        .I1(\txeq_txcoeff[0]_i_2_n_0 ),
        .I2(fsm_tx[1]),
        .I3(fsm_tx[0]),
        .I4(\txeq_txcoeff_reg_n_0_[6] ),
        .O(\txeq_txcoeff[0]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[0]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[6] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[7] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[0]),
        .O(\txeq_txcoeff[0]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[10]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[9] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[10]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[16] ),
        .O(\txeq_txcoeff[10]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[10]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[16] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[17] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[10]),
        .O(\txeq_txcoeff[10]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[11]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[10] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[11]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[17] ),
        .O(\txeq_txcoeff[11]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[11]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[17] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(in7),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[11]),
        .O(\txeq_txcoeff[11]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[12]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[11] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[12]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(in7),
        .O(\txeq_txcoeff[12]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[12]_i_2 
       (.I0(in7),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[0]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[12]),
        .O(\txeq_txcoeff[12]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[13]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[12] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[13]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_deemph_reg2[0]),
        .O(\txeq_txcoeff[13]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[13]_i_2 
       (.I0(txeq_deemph_reg2[0]),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[13]),
        .O(\txeq_txcoeff[13]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[14]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[13] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[14]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_deemph_reg2[1]),
        .O(\txeq_txcoeff[14]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[14]_i_2 
       (.I0(txeq_deemph_reg2[1]),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[2]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[14]),
        .O(\txeq_txcoeff[14]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[15]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[14] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[15]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_deemph_reg2[2]),
        .O(\txeq_txcoeff[15]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[15]_i_2 
       (.I0(txeq_deemph_reg2[2]),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[3]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[15]),
        .O(\txeq_txcoeff[15]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[16]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[15] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[16]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_deemph_reg2[3]),
        .O(\txeq_txcoeff[16]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[16]_i_2 
       (.I0(txeq_deemph_reg2[3]),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[4]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[16]),
        .O(\txeq_txcoeff[16]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[17]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[16] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[17]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(txeq_deemph_reg2[4]),
        .O(\txeq_txcoeff[17]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[17]_i_2 
       (.I0(txeq_deemph_reg2[4]),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(txeq_deemph_reg2[5]),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[17]),
        .O(\txeq_txcoeff[17]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'hFF040FFF)) 
    \txeq_txcoeff[18]_i_1 
       (.I0(txeq_control_reg2[0]),
        .I1(txeq_control_reg2[1]),
        .I2(fsm_tx[2]),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .O(txeq_txcoeff));
  LUT6 #(
    .INIT(64'h22F3220022002200)) 
    \txeq_txcoeff[18]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[17] ),
        .I1(fsm_tx[1]),
        .I2(\txeq_txcoeff[18]_i_3_n_0 ),
        .I3(fsm_tx[2]),
        .I4(txeq_deemph_reg2[5]),
        .I5(fsm_tx[0]),
        .O(\txeq_txcoeff[18]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair40" *) 
  LUT2 #(
    .INIT(4'hB)) 
    \txeq_txcoeff[18]_i_3 
       (.I0(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .O(\txeq_txcoeff[18]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[1]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[0] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[1]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[7] ),
        .O(\txeq_txcoeff[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[1]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[7] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[8] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[1]),
        .O(\txeq_txcoeff[1]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[2]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[1] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[2]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[8] ),
        .O(\txeq_txcoeff[2]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[2]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[8] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[9] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[2]),
        .O(\txeq_txcoeff[2]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[3]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[2] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[3]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[9] ),
        .O(\txeq_txcoeff[3]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[3]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[9] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[10] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[3]),
        .O(\txeq_txcoeff[3]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h2F20)) 
    \txeq_txcoeff[4]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[3] ),
        .I1(fsm_tx[1]),
        .I2(fsm_tx[2]),
        .I3(\txeq_txcoeff[4]_i_2_n_0 ),
        .O(\txeq_txcoeff[4]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hCACCCCCC00000000)) 
    \txeq_txcoeff[4]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[11] ),
        .I1(\txeq_txcoeff_reg_n_0_[10] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I3(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I4(fsm_tx[1]),
        .I5(fsm_tx[0]),
        .O(\txeq_txcoeff[4]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h2F20)) 
    \txeq_txcoeff[5]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[4] ),
        .I1(fsm_tx[1]),
        .I2(fsm_tx[2]),
        .I3(\txeq_txcoeff[5]_i_2_n_0 ),
        .O(\txeq_txcoeff[5]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hCACCCCCC00000000)) 
    \txeq_txcoeff[5]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[12] ),
        .I1(\txeq_txcoeff_reg_n_0_[11] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I3(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I4(fsm_tx[1]),
        .I5(fsm_tx[0]),
        .O(\txeq_txcoeff[5]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h2F20)) 
    \txeq_txcoeff[6]_i_1 
       (.I0(in10),
        .I1(fsm_tx[1]),
        .I2(fsm_tx[2]),
        .I3(\txeq_txcoeff[6]_i_2_n_0 ),
        .O(\txeq_txcoeff[6]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hCACCCCCC00000000)) 
    \txeq_txcoeff[6]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[13] ),
        .I1(\txeq_txcoeff_reg_n_0_[12] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I3(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I4(fsm_tx[1]),
        .I5(fsm_tx[0]),
        .O(\txeq_txcoeff[6]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[7]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[6] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[7]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[13] ),
        .O(\txeq_txcoeff[7]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[7]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[13] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[14] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[7]),
        .O(\txeq_txcoeff[7]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[8]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[7] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[8]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[14] ),
        .O(\txeq_txcoeff[8]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[8]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[14] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[15] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[8]),
        .O(\txeq_txcoeff[8]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h30BB308830883088)) 
    \txeq_txcoeff[9]_i_1 
       (.I0(\txeq_txcoeff_reg_n_0_[8] ),
        .I1(fsm_tx[2]),
        .I2(\txeq_txcoeff[9]_i_2_n_0 ),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[0]),
        .I5(\txeq_txcoeff_reg_n_0_[15] ),
        .O(\txeq_txcoeff[9]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hBA8AFFFFBA8A0000)) 
    \txeq_txcoeff[9]_i_2 
       (.I0(\txeq_txcoeff_reg_n_0_[15] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I3(\txeq_txcoeff_reg_n_0_[16] ),
        .I4(fsm_tx[0]),
        .I5(txeq_preset[9]),
        .O(\txeq_txcoeff[9]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h000004000F000400)) 
    \txeq_txcoeff_cnt[0]_i_1 
       (.I0(txeq_control_reg2[0]),
        .I1(txeq_control_reg2[1]),
        .I2(fsm_tx[2]),
        .I3(fsm_tx[0]),
        .I4(fsm_tx[1]),
        .I5(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .O(txeq_txcoeff_cnt[0]));
  (* SOFT_HLUTNM = "soft_lutpair31" *) 
  LUT5 #(
    .INIT(32'h00006000)) 
    \txeq_txcoeff_cnt[1]_i_1 
       (.I0(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .I1(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .I2(fsm_tx[0]),
        .I3(fsm_tx[1]),
        .I4(fsm_tx[2]),
        .O(txeq_txcoeff_cnt[1]));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_txcoeff_cnt[0]),
        .Q(\txeq_txcoeff_cnt_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txeq_txcoeff_cnt[1]),
        .Q(\txeq_txcoeff_cnt_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[0] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[0]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[10] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[10]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[10] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[11] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[11]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[11] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[12] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[12]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[12] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[13] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[13]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[13] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[14] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[14]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[14] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[15] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[15]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[15] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[16] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[16]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[16] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[17] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[17]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[17] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[18] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[18]_i_2_n_0 ),
        .Q(in7),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[1] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[1]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[2] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[2]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[3] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[3]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[3] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[4] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[4]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[4] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[5] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[5]_i_1_n_0 ),
        .Q(in10),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[6] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[6]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[6] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[7] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[7]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[7] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[8] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[8]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[8] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \txeq_txcoeff_reg[9] 
       (.C(pipe_pclk_in),
        .CE(txeq_txcoeff),
        .D(\txeq_txcoeff[9]_i_1_n_0 ),
        .Q(\txeq_txcoeff_reg_n_0_[9] ),
        .R(rst_cpllreset));
endmodule

module pcie_7x_bridge_pipe_sync
   (out,
    txphaligndone_reg3_reg_0,
    txphinitdone_reg2_reg_0,
    txphinitdone_reg3_reg_0,
    txsync_done,
    sync_txdlyen,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ,
    rst_cpllreset,
    txphaligndone0,
    pipe_pclk_in,
    SYNC_TXSYNC_START0,
    pipe_mmcm_lock_in,
    txdlysresetdone_reg1_reg_0,
    SYNC_TXPHINITDONE1,
    Q,
    gt_rx_elec_idle_wire_filter,
    user_rxcdrlock,
    gt_txsyncdone,
    rxdlysresetdone_reg1_reg_0,
    rxphaligndone_m_reg1_reg_0,
    rxsyncdone_reg1_reg_0,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_2 ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_0 ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_1 );
  output out;
  output txphaligndone_reg3_reg_0;
  output txphinitdone_reg2_reg_0;
  output txphinitdone_reg3_reg_0;
  output txsync_done;
  output sync_txdlyen;
  output [2:0]\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ;
  input rst_cpllreset;
  input txphaligndone0;
  input pipe_pclk_in;
  input SYNC_TXSYNC_START0;
  input pipe_mmcm_lock_in;
  input txdlysresetdone_reg1_reg_0;
  input SYNC_TXPHINITDONE1;
  input [0:0]Q;
  input [0:0]gt_rx_elec_idle_wire_filter;
  input user_rxcdrlock;
  input gt_txsyncdone;
  input rxdlysresetdone_reg1_reg_0;
  input rxphaligndone_m_reg1_reg_0;
  input rxsyncdone_reg1_reg_0;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_2 ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_0 ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_1 ;

  wire \FSM_onehot_txsync_fsm.fsm_tx[1]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[1]_i_2_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[2]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[3]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[4]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[5]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx[6]_i_1_n_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ;
  wire [2:0]\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_2 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[6]_1 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[2] ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ;
  wire [0:0]Q;
  wire SYNC_TXPHINITDONE1;
  wire SYNC_TXSYNC_START0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg2;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire gt_txsyncdone;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg2;
  wire pipe_mmcm_lock_in;
  wire pipe_pclk_in;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg2;
  wire rst_cpllreset;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxdlysresetdone_reg1;
  wire rxdlysresetdone_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxdlysresetdone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxelecidle_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxelecidle_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxphaligndone_m_reg1;
  wire rxphaligndone_m_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxphaligndone_m_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxphaligndone_s_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxphaligndone_s_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsync_donem_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsync_donem_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsync_start_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsync_start_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsyncdone_reg1;
  wire rxsyncdone_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxsyncdone_reg2;
  wire sync_txdlyen;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txdlysresetdone_reg1;
  wire txdlysresetdone_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txdlysresetdone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txdlysresetdone_reg3;
  wire txphaligndone0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphaligndone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphaligndone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphaligndone_reg3;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphinitdone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphinitdone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txphinitdone_reg3;
  wire txsync_done;
  wire \txsync_fsm.txdlyen_i_1_n_0 ;
  wire \txsync_fsm.txsync_done_i_1_n_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_start_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_start_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsync_start_reg3;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsyncdone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsyncdone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txsyncdone_reg3;
  wire user_rxcdrlock;

  assign out = txphaligndone_reg2;
  assign txphaligndone_reg3_reg_0 = txphaligndone_reg3;
  assign txphinitdone_reg2_reg_0 = txphinitdone_reg2;
  assign txphinitdone_reg3_reg_0 = txphinitdone_reg3;
  LUT5 #(
    .INIT(32'h1D1DFF1D)) 
    \FSM_onehot_txsync_fsm.fsm_tx[1]_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_2_n_0 ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ),
        .I2(txsync_start_reg2),
        .I3(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .I4(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    \FSM_onehot_txsync_fsm.fsm_tx[1]_i_2 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [1]),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[2] ),
        .I3(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [0]),
        .I4(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [2]),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_txsync_fsm.fsm_tx[2]_i_1 
       (.I0(mmcm_lock_reg2),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[2] ),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ),
        .I3(txsync_start_reg2),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[2]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFFD0D0D0)) 
    \FSM_onehot_txsync_fsm.fsm_tx[3]_i_1 
       (.I0(txdlysresetdone_reg2),
        .I1(txdlysresetdone_reg3),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [0]),
        .I3(mmcm_lock_reg2),
        .I4(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[2] ),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[3]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'h44F44444)) 
    \FSM_onehot_txsync_fsm.fsm_tx[4]_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [1]),
        .I2(txdlysresetdone_reg2),
        .I3(txdlysresetdone_reg3),
        .I4(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [0]),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[4]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hF8FFF8F888888888)) 
    \FSM_onehot_txsync_fsm.fsm_tx[5]_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [2]),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_2 ),
        .I3(txphinitdone_reg3),
        .I4(txphinitdone_reg2),
        .I5(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [1]),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[5]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hEAFFEAEA2A002A2A)) 
    \FSM_onehot_txsync_fsm.fsm_tx[6]_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg[6]_0 ),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg[6]_1 ),
        .I3(txphaligndone_reg3),
        .I4(txphaligndone_reg2),
        .I5(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [2]),
        .O(\FSM_onehot_txsync_fsm.fsm_tx[6]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDSE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[2]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[2] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[3]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [0]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[4]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [1]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[5]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 [2]),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:0000100,FSM_TXSYNC_START:0001000,FSM_TXPHINITDONE:0010000,FSM_TXSYNC_DONE1:0100000,FSM_TXSYNC_DONE2:1000000,FSM_TXSYNC_IDLE:0000010,iSTATE:0000001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_txsync_fsm.fsm_tx_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_txsync_fsm.fsm_tx[6]_i_1_n_0 ),
        .Q(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(gen3_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gen3_reg1),
        .Q(gen3_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_mmcm_lock_in),
        .Q(mmcm_lock_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(mmcm_lock_reg1),
        .Q(mmcm_lock_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_idle_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(Q),
        .Q(rate_idle_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_idle_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_idle_reg1),
        .Q(rate_idle_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxcdrlock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(user_rxcdrlock),
        .Q(rxcdrlock_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxcdrlock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxcdrlock_reg1),
        .Q(rxcdrlock_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxdlysresetdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxdlysresetdone_reg1_reg_0),
        .Q(rxdlysresetdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxdlysresetdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxdlysresetdone_reg1),
        .Q(rxdlysresetdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxelecidle_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rx_elec_idle_wire_filter),
        .Q(rxelecidle_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxelecidle_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxelecidle_reg1),
        .Q(rxelecidle_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxphaligndone_m_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxphaligndone_m_reg1_reg_0),
        .Q(rxphaligndone_m_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxphaligndone_m_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxphaligndone_m_reg1),
        .Q(rxphaligndone_m_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxphaligndone_s_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxphaligndone_s_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxphaligndone_s_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxphaligndone_s_reg1),
        .Q(rxphaligndone_s_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsync_donem_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxsync_donem_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsync_donem_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxsync_donem_reg1),
        .Q(rxsync_donem_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsync_start_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rxsync_start_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsync_start_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxsync_start_reg1),
        .Q(rxsync_start_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsyncdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxsyncdone_reg1_reg_0),
        .Q(rxsyncdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxsyncdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxsyncdone_reg1),
        .Q(rxsyncdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txdlysresetdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txdlysresetdone_reg1_reg_0),
        .Q(txdlysresetdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txdlysresetdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txdlysresetdone_reg1),
        .Q(txdlysresetdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txdlysresetdone_reg3_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txdlysresetdone_reg2),
        .Q(txdlysresetdone_reg3),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphaligndone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txphaligndone0),
        .Q(txphaligndone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphaligndone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txphaligndone_reg1),
        .Q(txphaligndone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphaligndone_reg3_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txphaligndone_reg2),
        .Q(txphaligndone_reg3),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphinitdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(SYNC_TXPHINITDONE1),
        .Q(txphinitdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphinitdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txphinitdone_reg1),
        .Q(txphinitdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txphinitdone_reg3_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txphinitdone_reg2),
        .Q(txphinitdone_reg3),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'hABAAA8AA)) 
    \txsync_fsm.txdlyen_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_2_n_0 ),
        .I2(txsync_start_reg2),
        .I3(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ),
        .I4(sync_txdlyen),
        .O(\txsync_fsm.txdlyen_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txsync_fsm.txdlyen_reg 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txsync_fsm.txdlyen_i_1_n_0 ),
        .Q(sync_txdlyen),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'h222F222222202222)) 
    \txsync_fsm.txsync_done_i_1 
       (.I0(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[6] ),
        .I1(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 ),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx[1]_i_2_n_0 ),
        .I3(txsync_start_reg2),
        .I4(\FSM_onehot_txsync_fsm.fsm_tx_reg_n_0_[1] ),
        .I5(txsync_done),
        .O(\txsync_fsm.txsync_done_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \txsync_fsm.txsync_done_reg 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txsync_fsm.txsync_done_i_1_n_0 ),
        .Q(txsync_done),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsync_start_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(SYNC_TXSYNC_START0),
        .Q(txsync_start_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsync_start_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_start_reg1),
        .Q(txsync_start_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsync_start_reg3_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsync_start_reg2),
        .Q(txsync_start_reg3),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsyncdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_txsyncdone),
        .Q(txsyncdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsyncdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsyncdone_reg1),
        .Q(txsyncdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txsyncdone_reg3_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txsyncdone_reg2),
        .Q(txsyncdone_reg3),
        .R(rst_cpllreset));
endmodule

module pcie_7x_bridge_pipe_user
   (out,
    txcompliance_reg2_reg_0,
    user_oobclk,
    user_rxbufreset,
    user_rxpcsreset,
    user_eyescanreset,
    user_rxcdrfreqreset,
    user_rxcdrreset,
    user_rxpmareset,
    gt_rxvalid_q12_out,
    reg_clock_locked_reg,
    gt_rx_phy_status_wire_filter,
    user_resetovrd,
    user_resetdone,
    user_rxcdrlock,
    txcompliance_reg2_reg_1,
    txcompliance_reg2_reg_2,
    SYNC_TXPHINITDONE1,
    rxsyncallin,
    txphaligndone0,
    txelecidle_reg2_reg_0,
    rst_cpllreset,
    pipe_pclk_sel_out,
    pipe_pclk_in,
    gt_rxresetdone,
    gt_txresetdone,
    pipe_tx0_elec_idle,
    pipe_tx0_compliance,
    gt_rxcdrlock,
    SR,
    gt_rxvalid,
    pipe_rxusrclk_in,
    PIPE_RXSTATUS,
    rst_idle_reg1_reg_0,
    Q,
    rxeq_adapt_done,
    pipe_oobclk_in,
    plm_in_l0__4,
    gt_rxvalid_q_reg,
    gt_rx_elec_idle_wire_filter,
    pipe_rx0_valid,
    reg_clock_locked,
    gt_phystatus,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[4] ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5] ,
    \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ,
    txphinitdone_reg1_reg,
    \gtp_channel.gtpe2_channel_i ,
    txphaligndone_reg1_reg);
  output out;
  output txcompliance_reg2_reg_0;
  output user_oobclk;
  output user_rxbufreset;
  output user_rxpcsreset;
  output user_eyescanreset;
  output user_rxcdrfreqreset;
  output user_rxcdrreset;
  output user_rxpmareset;
  output gt_rxvalid_q12_out;
  output reg_clock_locked_reg;
  output [0:0]gt_rx_phy_status_wire_filter;
  output user_resetovrd;
  output user_resetdone;
  output user_rxcdrlock;
  output txcompliance_reg2_reg_1;
  output txcompliance_reg2_reg_2;
  output SYNC_TXPHINITDONE1;
  output rxsyncallin;
  output txphaligndone0;
  output txelecidle_reg2_reg_0;
  input rst_cpllreset;
  input [0:0]pipe_pclk_sel_out;
  input pipe_pclk_in;
  input gt_rxresetdone;
  input gt_txresetdone;
  input pipe_tx0_elec_idle;
  input pipe_tx0_compliance;
  input gt_rxcdrlock;
  input [0:0]SR;
  input gt_rxvalid;
  input pipe_rxusrclk_in;
  input [0:0]PIPE_RXSTATUS;
  input [0:0]rst_idle_reg1_reg_0;
  input [1:0]Q;
  input rxeq_adapt_done;
  input pipe_oobclk_in;
  input plm_in_l0__4;
  input gt_rxvalid_q_reg;
  input [0:0]gt_rx_elec_idle_wire_filter;
  input pipe_rx0_valid;
  input reg_clock_locked;
  input gt_phystatus;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[4] ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[5] ;
  input \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ;
  input txphinitdone_reg1_reg;
  input \gtp_channel.gtpe2_channel_i ;
  input txphaligndone_reg1_reg;

  wire \FSM_onehot_resetovrd.fsm[0]_i_1_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[0]_i_2_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[1]_i_1_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[1]_i_2_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[2]_i_1_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[3]_i_1_n_0 ;
  wire \FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ;
  wire \FSM_onehot_resetovrd.fsm_reg_n_0_[0] ;
  wire \FSM_onehot_resetovrd.fsm_reg_n_0_[1] ;
  wire \FSM_onehot_resetovrd.fsm_reg_n_0_[2] ;
  wire \FSM_onehot_resetovrd.fsm_reg_n_0_[3] ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[4] ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[5] ;
  wire \FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ;
  wire [0:0]PIPE_RXSTATUS;
  wire [1:0]Q;
  wire [0:0]SR;
  wire SYNC_TXPHINITDONE1;
  wire gt_phystatus;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire [0:0]gt_rx_phy_status_wire_filter;
  wire gt_rxcdrlock;
  wire gt_rxresetdone;
  wire gt_rxvalid;
  wire gt_rxvalid_q12_out;
  wire gt_rxvalid_q_i_3_n_0;
  wire gt_rxvalid_q_reg;
  wire gt_txresetdone;
  wire \gtp_channel.gtpe2_channel_i ;
  wire [1:0]oobclk_cnt;
  wire \oobclk_div.oobclk_cnt[0]_i_1_n_0 ;
  wire \oobclk_div.oobclk_cnt[1]_i_1_n_0 ;
  wire \oobclk_div.oobclk_i_1_n_0 ;
  wire [3:0]p_0_in;
  wire [3:0]p_0_in__2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire pclk_sel_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire pclk_sel_reg2;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire pipe_rx0_valid;
  wire pipe_rxusrclk_in;
  wire pipe_tx0_compliance;
  wire pipe_tx0_elec_idle;
  wire plm_in_l0__4;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_done_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_gen3_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_gen3_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_idle_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_rxsync_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rate_rxsync_reg2;
  wire reg_clock_locked;
  wire reg_clock_locked_reg;
  wire [7:0]reset_cnt0;
  wire \resetovrd.reset[0]_i_1_n_0 ;
  wire \resetovrd.reset[1]_i_1_n_0 ;
  wire \resetovrd.reset[2]_i_1_n_0 ;
  wire \resetovrd.reset[3]_i_1_n_0 ;
  wire \resetovrd.reset[4]_i_1_n_0 ;
  wire \resetovrd.reset[5]_i_1_n_0 ;
  wire \resetovrd.reset[6]_i_1_n_0 ;
  wire \resetovrd.reset[7]_i_1_n_0 ;
  wire \resetovrd.reset[7]_i_2_n_0 ;
  wire \resetovrd.reset_cnt[1]_i_1_n_0 ;
  wire \resetovrd.reset_cnt[4]_i_1_n_0 ;
  wire \resetovrd.reset_cnt[7]_i_1_n_0 ;
  wire [7:0]\resetovrd.reset_cnt_reg ;
  wire \resetovrd.reset_reg_n_0_[7] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire resetovrd_start_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire resetovrd_start_reg2;
  wire rst_cpllreset;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rst_idle_reg1;
  wire [0:0]rst_idle_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rst_idle_reg2;
  wire [3:0]rxcdrlock_cnt_reg;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxcdrlock_reg2;
  wire rxeq_adapt_done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_adapt_done_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxeq_adapt_done_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxresetdone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxresetdone_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxstatus_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxstatus_reg2;
  wire rxsyncallin;
  wire [3:0]rxvalid_cnt_reg;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxvalid_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rxvalid_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txcompliance_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txcompliance_reg2;
  wire txcompliance_reg2_reg_1;
  wire txcompliance_reg2_reg_2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txelecidle_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txelecidle_reg2;
  wire txelecidle_reg2_reg_0;
  wire txphaligndone0;
  wire txphaligndone_reg1_reg;
  wire txphinitdone_reg1_reg;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txresetdone_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire txresetdone_reg2;
  wire user_eyescanreset;
  wire user_oobclk;
  wire user_resetdone;
  wire user_resetovrd;
  wire user_rxbufreset;
  wire user_rxcdrfreqreset;
  wire user_rxcdrlock;
  wire user_rxcdrreset;
  wire user_rxdfelpmreset;
  wire user_rxpcsreset;
  wire user_rxpmareset;

  assign out = txelecidle_reg2;
  assign txcompliance_reg2_reg_0 = txcompliance_reg2;
  LUT6 #(
    .INIT(64'hFFFFFFFEAAAAAAAA)) 
    \FSM_onehot_resetovrd.fsm[0]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_eyescanreset),
        .I2(user_rxpcsreset),
        .I3(user_rxpmareset),
        .I4(\FSM_onehot_resetovrd.fsm[0]_i_2_n_0 ),
        .I5(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .O(\FSM_onehot_resetovrd.fsm[0]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFEFF)) 
    \FSM_onehot_resetovrd.fsm[0]_i_2 
       (.I0(user_rxbufreset),
        .I1(user_rxcdrfreqreset),
        .I2(\resetovrd.reset_reg_n_0_[7] ),
        .I3(rxresetdone_reg2),
        .I4(user_rxcdrreset),
        .I5(user_rxdfelpmreset),
        .O(\FSM_onehot_resetovrd.fsm[0]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_resetovrd.fsm[1]_i_1 
       (.I0(resetovrd_start_reg2),
        .I1(\FSM_onehot_resetovrd.fsm_reg_n_0_[1] ),
        .I2(\FSM_onehot_resetovrd.fsm[1]_i_2_n_0 ),
        .I3(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .O(\FSM_onehot_resetovrd.fsm[1]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair52" *) 
  LUT4 #(
    .INIT(16'h0001)) 
    \FSM_onehot_resetovrd.fsm[1]_i_2 
       (.I0(user_eyescanreset),
        .I1(user_rxpcsreset),
        .I2(user_rxpmareset),
        .I3(\FSM_onehot_resetovrd.fsm[0]_i_2_n_0 ),
        .O(\FSM_onehot_resetovrd.fsm[1]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h0000000000000002)) 
    \FSM_onehot_resetovrd.fsm[2]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[3] ),
        .I1(\resetovrd.reset_cnt_reg [5]),
        .I2(\resetovrd.reset_cnt_reg [4]),
        .I3(\resetovrd.reset_cnt_reg [7]),
        .I4(\resetovrd.reset_cnt_reg [6]),
        .I5(\FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ),
        .O(\FSM_onehot_resetovrd.fsm[2]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair51" *) 
  LUT4 #(
    .INIT(16'hFFFE)) 
    \FSM_onehot_resetovrd.fsm[2]_i_2 
       (.I0(\resetovrd.reset_cnt_reg [3]),
        .I1(\resetovrd.reset_cnt_reg [0]),
        .I2(\resetovrd.reset_cnt_reg [1]),
        .I3(\resetovrd.reset_cnt_reg [2]),
        .O(\FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'hF444)) 
    \FSM_onehot_resetovrd.fsm[3]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ),
        .I1(\FSM_onehot_resetovrd.fsm_reg_n_0_[3] ),
        .I2(resetovrd_start_reg2),
        .I3(\FSM_onehot_resetovrd.fsm_reg_n_0_[1] ),
        .O(\FSM_onehot_resetovrd.fsm[3]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair50" *) 
  LUT5 #(
    .INIT(32'h00000001)) 
    \FSM_onehot_resetovrd.fsm[3]_i_2 
       (.I0(\FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ),
        .I1(\resetovrd.reset_cnt_reg [6]),
        .I2(\resetovrd.reset_cnt_reg [7]),
        .I3(\resetovrd.reset_cnt_reg [4]),
        .I4(\resetovrd.reset_cnt_reg [5]),
        .O(\FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_RESETOVRD:1000,FSM_RESET_INIT:0100,FSM_RESET:0001,FSM_IDLE:0010" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_resetovrd.fsm_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_resetovrd.fsm[0]_i_1_n_0 ),
        .Q(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RESETOVRD:1000,FSM_RESET_INIT:0100,FSM_RESET:0001,FSM_IDLE:0010" *) 
  FDSE #(
    .INIT(1'b1)) 
    \FSM_onehot_resetovrd.fsm_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_resetovrd.fsm[1]_i_1_n_0 ),
        .Q(\FSM_onehot_resetovrd.fsm_reg_n_0_[1] ),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RESETOVRD:1000,FSM_RESET_INIT:0100,FSM_RESET:0001,FSM_IDLE:0010" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_resetovrd.fsm_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_resetovrd.fsm[2]_i_1_n_0 ),
        .Q(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_RESETOVRD:1000,FSM_RESET_INIT:0100,FSM_RESET:0001,FSM_IDLE:0010" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_resetovrd.fsm_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_resetovrd.fsm[3]_i_1_n_0 ),
        .Q(\FSM_onehot_resetovrd.fsm_reg_n_0_[3] ),
        .R(rst_cpllreset));
  LUT4 #(
    .INIT(16'h8F88)) 
    \FSM_onehot_txsync_fsm.fsm_tx[4]_i_2 
       (.I0(txcompliance_reg2),
        .I1(txelecidle_reg2),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg[4] ),
        .I3(\FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 ),
        .O(txcompliance_reg2_reg_1));
  LUT4 #(
    .INIT(16'h7077)) 
    \FSM_onehot_txsync_fsm.fsm_tx[5]_i_2 
       (.I0(txcompliance_reg2),
        .I1(txelecidle_reg2),
        .I2(\FSM_onehot_txsync_fsm.fsm_tx_reg[5] ),
        .I3(\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ),
        .O(txcompliance_reg2_reg_2));
  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_txsync_fsm.fsm_tx[5]_i_3 
       (.I0(txelecidle_reg2),
        .I1(txcompliance_reg2),
        .O(txelecidle_reg2_reg_0));
  LUT5 #(
    .INIT(32'hFFFFA8FF)) 
    gt_rx_phy_status_q_i_1
       (.I0(gt_phystatus),
        .I1(rate_rxsync_reg2),
        .I2(rate_idle_reg2),
        .I3(rst_idle_reg2),
        .I4(rate_done_reg2),
        .O(gt_rx_phy_status_wire_filter));
  LUT6 #(
    .INIT(64'h0000800080008000)) 
    gt_rxvalid_q_i_2
       (.I0(rxvalid_cnt_reg[1]),
        .I1(rxvalid_cnt_reg[0]),
        .I2(rxvalid_cnt_reg[2]),
        .I3(gt_rxvalid_q_i_3_n_0),
        .I4(plm_in_l0__4),
        .I5(gt_rxvalid_q_reg),
        .O(gt_rxvalid_q12_out));
  LUT6 #(
    .INIT(64'h8000800000008000)) 
    gt_rxvalid_q_i_3
       (.I0(rate_idle_reg2),
        .I1(rst_idle_reg2),
        .I2(gt_rxvalid),
        .I3(rxvalid_cnt_reg[3]),
        .I4(gt_rx_elec_idle_wire_filter),
        .I5(pipe_rx0_valid),
        .O(gt_rxvalid_q_i_3_n_0));
  LUT1 #(
    .INIT(2'h1)) 
    \gtp_channel.gtpe2_channel_i_i_3 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[1] ),
        .O(user_resetovrd));
  LUT3 #(
    .INIT(8'hEA)) 
    \gtp_channel.gtpe2_channel_i_i_4 
       (.I0(\gtp_channel.gtpe2_channel_i ),
        .I1(txcompliance_reg2),
        .I2(txelecidle_reg2),
        .O(rxsyncallin));
  LUT3 #(
    .INIT(8'hEA)) 
    \gtp_channel.gtpe2_channel_i_i_5 
       (.I0(txphaligndone_reg1_reg),
        .I1(txcompliance_reg2),
        .I2(txelecidle_reg2),
        .O(txphaligndone0));
  (* SOFT_HLUTNM = "soft_lutpair54" *) 
  LUT2 #(
    .INIT(4'h1)) 
    \oobclk_div.oobclk_cnt[0]_i_1 
       (.I0(oobclk_cnt[0]),
        .I1(rst_cpllreset),
        .O(\oobclk_div.oobclk_cnt[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair54" *) 
  LUT3 #(
    .INIT(8'h06)) 
    \oobclk_div.oobclk_cnt[1]_i_1 
       (.I0(oobclk_cnt[1]),
        .I1(oobclk_cnt[0]),
        .I2(rst_cpllreset),
        .O(\oobclk_div.oobclk_cnt[1]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \oobclk_div.oobclk_cnt_reg[0] 
       (.C(pipe_oobclk_in),
        .CE(1'b1),
        .D(\oobclk_div.oobclk_cnt[0]_i_1_n_0 ),
        .Q(oobclk_cnt[0]),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \oobclk_div.oobclk_cnt_reg[1] 
       (.C(pipe_oobclk_in),
        .CE(1'b1),
        .D(\oobclk_div.oobclk_cnt[1]_i_1_n_0 ),
        .Q(oobclk_cnt[1]),
        .R(1'b0));
  LUT4 #(
    .INIT(16'h00E2)) 
    \oobclk_div.oobclk_i_1 
       (.I0(oobclk_cnt[0]),
        .I1(pclk_sel_reg2),
        .I2(oobclk_cnt[1]),
        .I3(rst_cpllreset),
        .O(\oobclk_div.oobclk_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \oobclk_div.oobclk_reg 
       (.C(pipe_oobclk_in),
        .CE(1'b1),
        .D(\oobclk_div.oobclk_i_1_n_0 ),
        .Q(user_oobclk),
        .R(1'b0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE pclk_sel_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_pclk_sel_out),
        .Q(pclk_sel_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE pclk_sel_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pclk_sel_reg1),
        .Q(pclk_sel_reg2),
        .R(rst_cpllreset));
  LUT2 #(
    .INIT(4'h2)) 
    phy_rdy_n_int_i_1
       (.I0(reg_clock_locked),
        .I1(rst_idle_reg2),
        .O(reg_clock_locked_reg));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_done_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(Q[1]),
        .Q(rate_done_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_done_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rate_done_reg1),
        .Q(rate_done_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_gen3_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rate_gen3_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_gen3_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rate_gen3_reg1),
        .Q(rate_gen3_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_idle_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(Q[0]),
        .Q(rate_idle_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_idle_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rate_idle_reg1),
        .Q(rate_idle_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_rxsync_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(rate_rxsync_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rate_rxsync_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rate_rxsync_reg1),
        .Q(rate_rxsync_reg2),
        .R(SR));
  LUT2 #(
    .INIT(4'h8)) 
    \resetdone_reg1[0]_i_1 
       (.I0(rxresetdone_reg2),
        .I1(txresetdone_reg2),
        .O(user_resetdone));
  LUT5 #(
    .INIT(32'h00F700F0)) 
    \resetovrd.reset[0]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ),
        .I1(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .I2(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I3(rst_cpllreset),
        .I4(user_rxpmareset),
        .O(\resetovrd.reset[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair58" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[1]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxpmareset),
        .O(\resetovrd.reset[1]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair58" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[2]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxcdrreset),
        .O(\resetovrd.reset[2]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair57" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[3]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxcdrfreqreset),
        .O(\resetovrd.reset[3]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair57" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[4]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxdfelpmreset),
        .O(\resetovrd.reset[4]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair52" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[5]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_eyescanreset),
        .O(\resetovrd.reset[5]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair56" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[6]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxpcsreset),
        .O(\resetovrd.reset[6]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hFFF8)) 
    \resetovrd.reset[7]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ),
        .I1(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .I2(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I3(rst_cpllreset),
        .O(\resetovrd.reset[7]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair56" *) 
  LUT2 #(
    .INIT(4'hE)) 
    \resetovrd.reset[7]_i_2 
       (.I0(\FSM_onehot_resetovrd.fsm_reg_n_0_[2] ),
        .I1(user_rxbufreset),
        .O(\resetovrd.reset[7]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair55" *) 
  LUT1 #(
    .INIT(2'h1)) 
    \resetovrd.reset_cnt[0]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [0]),
        .O(reset_cnt0[0]));
  (* SOFT_HLUTNM = "soft_lutpair55" *) 
  LUT2 #(
    .INIT(4'h9)) 
    \resetovrd.reset_cnt[1]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [0]),
        .I1(\resetovrd.reset_cnt_reg [1]),
        .O(\resetovrd.reset_cnt[1]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair53" *) 
  LUT3 #(
    .INIT(8'hE1)) 
    \resetovrd.reset_cnt[2]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [0]),
        .I1(\resetovrd.reset_cnt_reg [1]),
        .I2(\resetovrd.reset_cnt_reg [2]),
        .O(reset_cnt0[2]));
  (* SOFT_HLUTNM = "soft_lutpair53" *) 
  LUT4 #(
    .INIT(16'hFE01)) 
    \resetovrd.reset_cnt[3]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [2]),
        .I1(\resetovrd.reset_cnt_reg [1]),
        .I2(\resetovrd.reset_cnt_reg [0]),
        .I3(\resetovrd.reset_cnt_reg [3]),
        .O(reset_cnt0[3]));
  (* SOFT_HLUTNM = "soft_lutpair51" *) 
  LUT5 #(
    .INIT(32'hAAAAAAA9)) 
    \resetovrd.reset_cnt[4]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [4]),
        .I1(\resetovrd.reset_cnt_reg [2]),
        .I2(\resetovrd.reset_cnt_reg [1]),
        .I3(\resetovrd.reset_cnt_reg [0]),
        .I4(\resetovrd.reset_cnt_reg [3]),
        .O(\resetovrd.reset_cnt[4]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'hAAAAAAAAAAAAAAA9)) 
    \resetovrd.reset_cnt[5]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [5]),
        .I1(\resetovrd.reset_cnt_reg [3]),
        .I2(\resetovrd.reset_cnt_reg [0]),
        .I3(\resetovrd.reset_cnt_reg [1]),
        .I4(\resetovrd.reset_cnt_reg [2]),
        .I5(\resetovrd.reset_cnt_reg [4]),
        .O(reset_cnt0[5]));
  LUT4 #(
    .INIT(16'hAAA9)) 
    \resetovrd.reset_cnt[6]_i_1 
       (.I0(\resetovrd.reset_cnt_reg [6]),
        .I1(\resetovrd.reset_cnt_reg [5]),
        .I2(\resetovrd.reset_cnt_reg [4]),
        .I3(\FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ),
        .O(reset_cnt0[6]));
  LUT4 #(
    .INIT(16'hFFAB)) 
    \resetovrd.reset_cnt[7]_i_1 
       (.I0(\FSM_onehot_resetovrd.fsm[3]_i_2_n_0 ),
        .I1(\FSM_onehot_resetovrd.fsm_reg_n_0_[0] ),
        .I2(\FSM_onehot_resetovrd.fsm_reg_n_0_[3] ),
        .I3(rst_cpllreset),
        .O(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair50" *) 
  LUT5 #(
    .INIT(32'hAAAAAAA9)) 
    \resetovrd.reset_cnt[7]_i_2 
       (.I0(\resetovrd.reset_cnt_reg [7]),
        .I1(\resetovrd.reset_cnt_reg [6]),
        .I2(\FSM_onehot_resetovrd.fsm[2]_i_2_n_0 ),
        .I3(\resetovrd.reset_cnt_reg [4]),
        .I4(\resetovrd.reset_cnt_reg [5]),
        .O(reset_cnt0[7]));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[0]),
        .Q(\resetovrd.reset_cnt_reg [0]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\resetovrd.reset_cnt[1]_i_1_n_0 ),
        .Q(\resetovrd.reset_cnt_reg [1]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[2]),
        .Q(\resetovrd.reset_cnt_reg [2]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[3]),
        .Q(\resetovrd.reset_cnt_reg [3]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\resetovrd.reset_cnt[4]_i_1_n_0 ),
        .Q(\resetovrd.reset_cnt_reg [4]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[5]),
        .Q(\resetovrd.reset_cnt_reg [5]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDSE #(
    .INIT(1'b1)) 
    \resetovrd.reset_cnt_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[6]),
        .Q(\resetovrd.reset_cnt_reg [6]),
        .S(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_cnt_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(reset_cnt0[7]),
        .Q(\resetovrd.reset_cnt_reg [7]),
        .R(\resetovrd.reset_cnt[7]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\resetovrd.reset[0]_i_1_n_0 ),
        .Q(user_rxpmareset),
        .R(1'b0));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[1] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[1]_i_1_n_0 ),
        .Q(user_rxcdrreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[2] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[2]_i_1_n_0 ),
        .Q(user_rxcdrfreqreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[3] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[3]_i_1_n_0 ),
        .Q(user_rxdfelpmreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[4] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[4]_i_1_n_0 ),
        .Q(user_eyescanreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[5] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[5]_i_1_n_0 ),
        .Q(user_rxpcsreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[6] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[6]_i_1_n_0 ),
        .Q(user_rxbufreset),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \resetovrd.reset_reg[7] 
       (.C(pipe_pclk_in),
        .CE(\resetovrd.reset[7]_i_1_n_0 ),
        .D(\resetovrd.reset[7]_i_2_n_0 ),
        .Q(\resetovrd.reset_reg_n_0_[7] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE resetovrd_start_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(resetovrd_start_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE resetovrd_start_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(resetovrd_start_reg1),
        .Q(resetovrd_start_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rst_idle_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rst_idle_reg1_reg_0),
        .Q(rst_idle_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rst_idle_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rst_idle_reg1),
        .Q(rst_idle_reg2),
        .R(SR));
  LUT5 #(
    .INIT(32'h8A0A0A0A)) 
    \rxcdrlock_cnt[0]_i_1 
       (.I0(rxcdrlock_reg2),
        .I1(rxcdrlock_cnt_reg[2]),
        .I2(rxcdrlock_cnt_reg[0]),
        .I3(rxcdrlock_cnt_reg[1]),
        .I4(rxcdrlock_cnt_reg[3]),
        .O(p_0_in__2[0]));
  LUT5 #(
    .INIT(32'hA8282828)) 
    \rxcdrlock_cnt[1]_i_1 
       (.I0(rxcdrlock_reg2),
        .I1(rxcdrlock_cnt_reg[0]),
        .I2(rxcdrlock_cnt_reg[1]),
        .I3(rxcdrlock_cnt_reg[2]),
        .I4(rxcdrlock_cnt_reg[3]),
        .O(p_0_in__2[1]));
  LUT5 #(
    .INIT(32'h8CCCC000)) 
    \rxcdrlock_cnt[2]_i_1 
       (.I0(rxcdrlock_cnt_reg[3]),
        .I1(rxcdrlock_reg2),
        .I2(rxcdrlock_cnt_reg[1]),
        .I3(rxcdrlock_cnt_reg[0]),
        .I4(rxcdrlock_cnt_reg[2]),
        .O(p_0_in__2[2]));
  LUT5 #(
    .INIT(32'hA8888888)) 
    \rxcdrlock_cnt[3]_i_1 
       (.I0(rxcdrlock_reg2),
        .I1(rxcdrlock_cnt_reg[3]),
        .I2(rxcdrlock_cnt_reg[1]),
        .I3(rxcdrlock_cnt_reg[0]),
        .I4(rxcdrlock_cnt_reg[2]),
        .O(p_0_in__2[3]));
  FDRE #(
    .INIT(1'b0)) 
    \rxcdrlock_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__2[0]),
        .Q(rxcdrlock_cnt_reg[0]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxcdrlock_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__2[1]),
        .Q(rxcdrlock_cnt_reg[1]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxcdrlock_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__2[2]),
        .Q(rxcdrlock_cnt_reg[2]),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \rxcdrlock_cnt_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(p_0_in__2[3]),
        .Q(rxcdrlock_cnt_reg[3]),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'h80000000)) 
    \rxcdrlock_reg1[0]_i_1 
       (.I0(gt_rxcdrlock),
        .I1(rxcdrlock_cnt_reg[3]),
        .I2(rxcdrlock_cnt_reg[1]),
        .I3(rxcdrlock_cnt_reg[0]),
        .I4(rxcdrlock_cnt_reg[2]),
        .O(user_rxcdrlock));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxcdrlock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rxcdrlock),
        .Q(rxcdrlock_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxcdrlock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxcdrlock_reg1),
        .Q(rxcdrlock_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_adapt_done_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_adapt_done),
        .Q(rxeq_adapt_done_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxeq_adapt_done_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_adapt_done_reg1),
        .Q(rxeq_adapt_done_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxresetdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_rxresetdone),
        .Q(rxresetdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxresetdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxresetdone_reg1),
        .Q(rxresetdone_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxstatus_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(PIPE_RXSTATUS),
        .Q(rxstatus_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxstatus_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rxstatus_reg1),
        .Q(rxstatus_reg2),
        .R(SR));
  LUT6 #(
    .INIT(64'hA022002200220022)) 
    \rxvalid_cnt[0]_i_1 
       (.I0(rxvalid_reg2),
        .I1(rxstatus_reg2),
        .I2(rxvalid_cnt_reg[1]),
        .I3(rxvalid_cnt_reg[0]),
        .I4(rxvalid_cnt_reg[2]),
        .I5(rxvalid_cnt_reg[3]),
        .O(p_0_in[0]));
  LUT6 #(
    .INIT(64'hA220022002200220)) 
    \rxvalid_cnt[1]_i_1 
       (.I0(rxvalid_reg2),
        .I1(rxstatus_reg2),
        .I2(rxvalid_cnt_reg[1]),
        .I3(rxvalid_cnt_reg[0]),
        .I4(rxvalid_cnt_reg[2]),
        .I5(rxvalid_cnt_reg[3]),
        .O(p_0_in[1]));
  LUT6 #(
    .INIT(64'hA222200002222000)) 
    \rxvalid_cnt[2]_i_1 
       (.I0(rxvalid_reg2),
        .I1(rxstatus_reg2),
        .I2(rxvalid_cnt_reg[1]),
        .I3(rxvalid_cnt_reg[0]),
        .I4(rxvalid_cnt_reg[2]),
        .I5(rxvalid_cnt_reg[3]),
        .O(p_0_in[2]));
  LUT6 #(
    .INIT(64'hA222222220000000)) 
    \rxvalid_cnt[3]_i_1 
       (.I0(rxvalid_reg2),
        .I1(rxstatus_reg2),
        .I2(rxvalid_cnt_reg[1]),
        .I3(rxvalid_cnt_reg[0]),
        .I4(rxvalid_cnt_reg[2]),
        .I5(rxvalid_cnt_reg[3]),
        .O(p_0_in[3]));
  FDRE #(
    .INIT(1'b0)) 
    \rxvalid_cnt_reg[0] 
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(p_0_in[0]),
        .Q(rxvalid_cnt_reg[0]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \rxvalid_cnt_reg[1] 
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(p_0_in[1]),
        .Q(rxvalid_cnt_reg[1]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \rxvalid_cnt_reg[2] 
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(p_0_in[2]),
        .Q(rxvalid_cnt_reg[2]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \rxvalid_cnt_reg[3] 
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(p_0_in[3]),
        .Q(rxvalid_cnt_reg[3]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxvalid_reg1_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(gt_rxvalid),
        .Q(rxvalid_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rxvalid_reg2_reg
       (.C(pipe_rxusrclk_in),
        .CE(1'b1),
        .D(rxvalid_reg1),
        .Q(rxvalid_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txcompliance_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_tx0_compliance),
        .Q(txcompliance_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txcompliance_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcompliance_reg1),
        .Q(txcompliance_reg2),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txelecidle_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_tx0_elec_idle),
        .Q(txelecidle_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txelecidle_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txelecidle_reg1),
        .Q(txelecidle_reg2),
        .R(rst_cpllreset));
  LUT3 #(
    .INIT(8'hEA)) 
    txphinitdone_reg1_i_1
       (.I0(txphinitdone_reg1_reg),
        .I1(txcompliance_reg2),
        .I2(txelecidle_reg2),
        .O(SYNC_TXPHINITDONE1));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txresetdone_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(gt_txresetdone),
        .Q(txresetdone_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE txresetdone_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txresetdone_reg1),
        .Q(txresetdone_reg2),
        .R(rst_cpllreset));
endmodule

module pcie_7x_bridge_pipe_wrapper
   (pci_exp_txn,
    pci_exp_txp,
    pipe_rx0_chanisaligned,
    gt_rx_elec_idle_wire_filter,
    pipe_rxoutclk_out,
    pipe_txoutclk_out,
    PIPE_RXSTATUS,
    \gtp_channel.gtpe2_channel_i ,
    D,
    pipe_pclk_sel_out,
    p_0_in_0,
    gt_rxvalid_q12_out,
    reg_clock_locked_reg,
    gt_rx_phy_status_wire_filter,
    pipe_dclk_in,
    sys_clk,
    pci_exp_rxn,
    pci_exp_rxp,
    pipe_rx0_polarity,
    pipe_rxusrclk_in,
    pipe_tx_deemph,
    pipe_tx_rcvr_det,
    pipe_tx0_elec_idle,
    pipe_pclk_in,
    pipe_tx0_powerdown,
    pipe_tx_margin,
    pipe_tx0_data,
    pipe_tx0_compliance,
    pipe_tx0_char_is_k,
    pipe_mmcm_lock_in,
    pipe_oobclk_in,
    reset_n_reg1_reg_0,
    plm_in_l0__4,
    gt_rxvalid_q_reg,
    pipe_rx0_valid,
    reg_clock_locked,
    \rate_reg1_reg[1] ,
    \rate_in_reg1_reg[1] );
  output [0:0]pci_exp_txn;
  output [0:0]pci_exp_txp;
  output pipe_rx0_chanisaligned;
  output [0:0]gt_rx_elec_idle_wire_filter;
  output [0:0]pipe_rxoutclk_out;
  output pipe_txoutclk_out;
  output [2:0]PIPE_RXSTATUS;
  output [15:0]\gtp_channel.gtpe2_channel_i ;
  output [1:0]D;
  output [0:0]pipe_pclk_sel_out;
  output p_0_in_0;
  output gt_rxvalid_q12_out;
  output reg_clock_locked_reg;
  output [0:0]gt_rx_phy_status_wire_filter;
  input pipe_dclk_in;
  input sys_clk;
  input [0:0]pci_exp_rxn;
  input [0:0]pci_exp_rxp;
  input pipe_rx0_polarity;
  input pipe_rxusrclk_in;
  input pipe_tx_deemph;
  input pipe_tx_rcvr_det;
  input pipe_tx0_elec_idle;
  input pipe_pclk_in;
  input [1:0]pipe_tx0_powerdown;
  input [2:0]pipe_tx_margin;
  input [15:0]pipe_tx0_data;
  input pipe_tx0_compliance;
  input [1:0]pipe_tx0_char_is_k;
  input pipe_mmcm_lock_in;
  input pipe_oobclk_in;
  input reset_n_reg1_reg_0;
  input plm_in_l0__4;
  input gt_rxvalid_q_reg;
  input pipe_rx0_valid;
  input reg_clock_locked;
  input [1:0]\rate_reg1_reg[1] ;
  input [1:0]\rate_in_reg1_reg[1] ;

  wire [1:0]D;
  wire DRP_START0;
  wire DRP_X160;
  wire [2:0]PIPE_RXSTATUS;
  wire SYNC_TXPHINITDONE1;
  wire SYNC_TXSYNC_START0;
  wire dclk_rst_reg2;
  wire done;
  wire [4:4]drp_mux_addr;
  wire [15:0]drp_mux_di;
  wire drp_mux_en;
  wire [6:0]eq_txeq_maincursor;
  wire [4:0]eq_txeq_postcursor;
  wire [4:0]eq_txeq_precursor;
  wire gt_cpllpdrefclk;
  wire gt_phystatus;
  wire [0:0]gt_rx_elec_idle_wire_filter;
  wire [0:0]gt_rx_phy_status_wire_filter;
  wire gt_rxcdrlock;
  wire gt_rxratedone;
  wire gt_rxresetdone;
  wire gt_rxvalid;
  wire gt_rxvalid_q12_out;
  wire gt_rxvalid_q_reg;
  wire gt_txratedone;
  wire gt_txresetdone;
  wire gt_txsyncdone;
  wire [15:0]\gtp_channel.gtpe2_channel_i ;
  wire \gtp_pipe_reset.gtp_pipe_reset_i_n_0 ;
  wire \gtp_pipe_reset.gtp_pipe_reset_i_n_10 ;
  wire p_0_in4_in;
  wire p_0_in_0;
  wire p_1_in;
  wire p_1_in0_in;
  wire p_1_in5_in;
  wire [0:0]pci_exp_rxn;
  wire [0:0]pci_exp_rxp;
  wire [0:0]pci_exp_txn;
  wire [0:0]pci_exp_txp;
  wire pipe_dclk_in;
  wire \pipe_lane[0].gt_wrapper_i_n_0 ;
  wire \pipe_lane[0].gt_wrapper_i_n_10 ;
  wire \pipe_lane[0].gt_wrapper_i_n_13 ;
  wire \pipe_lane[0].gt_wrapper_i_n_15 ;
  wire \pipe_lane[0].gt_wrapper_i_n_17 ;
  wire \pipe_lane[0].gt_wrapper_i_n_18 ;
  wire \pipe_lane[0].gt_wrapper_i_n_22 ;
  wire \pipe_lane[0].gt_wrapper_i_n_23 ;
  wire \pipe_lane[0].gt_wrapper_i_n_24 ;
  wire \pipe_lane[0].gt_wrapper_i_n_25 ;
  wire \pipe_lane[0].gt_wrapper_i_n_26 ;
  wire \pipe_lane[0].gt_wrapper_i_n_27 ;
  wire \pipe_lane[0].gt_wrapper_i_n_28 ;
  wire \pipe_lane[0].gt_wrapper_i_n_29 ;
  wire \pipe_lane[0].gt_wrapper_i_n_30 ;
  wire \pipe_lane[0].gt_wrapper_i_n_31 ;
  wire \pipe_lane[0].gt_wrapper_i_n_32 ;
  wire \pipe_lane[0].gt_wrapper_i_n_33 ;
  wire \pipe_lane[0].gt_wrapper_i_n_34 ;
  wire \pipe_lane[0].gt_wrapper_i_n_35 ;
  wire \pipe_lane[0].gt_wrapper_i_n_36 ;
  wire \pipe_lane[0].gt_wrapper_i_n_37 ;
  wire \pipe_lane[0].gt_wrapper_i_n_6 ;
  wire \pipe_lane[0].gt_wrapper_i_n_9 ;
  wire \pipe_lane[0].gtp_pipe_drp.gtp_pipe_drp_i_n_1 ;
  wire \pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i_n_5 ;
  wire \pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_1 ;
  wire \pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_2 ;
  wire \pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_3 ;
  wire \pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_4 ;
  wire \pipe_lane[0].pipe_sync_i_n_1 ;
  wire \pipe_lane[0].pipe_sync_i_n_3 ;
  wire \pipe_lane[0].pipe_sync_i_n_6 ;
  wire \pipe_lane[0].pipe_sync_i_n_7 ;
  wire \pipe_lane[0].pipe_sync_i_n_8 ;
  wire \pipe_lane[0].pipe_user_i_n_15 ;
  wire \pipe_lane[0].pipe_user_i_n_16 ;
  wire \pipe_lane[0].pipe_user_i_n_20 ;
  wire pipe_mmcm_lock_in;
  wire pipe_oobclk_in;
  wire pipe_pclk_in;
  wire [0:0]pipe_pclk_sel_out;
  wire pipe_rx0_chanisaligned;
  wire pipe_rx0_polarity;
  wire pipe_rx0_valid;
  wire [0:0]pipe_rxoutclk_out;
  wire pipe_rxusrclk_in;
  wire [1:0]pipe_tx0_char_is_k;
  wire pipe_tx0_compliance;
  wire [15:0]pipe_tx0_data;
  wire pipe_tx0_elec_idle;
  wire [1:0]pipe_tx0_powerdown;
  wire pipe_tx_deemph;
  wire [2:0]pipe_tx_margin;
  wire pipe_tx_rcvr_det;
  wire pipe_txoutclk_out;
  wire plm_in_l0__4;
  wire \qpll_wrapper_i/PLL0RESET0 ;
  wire \qpll_wrapper_i/cpllrst ;
  wire qrst_drp_start;
  wire rate_done;
  wire [1:0]\rate_in_reg1_reg[1] ;
  wire [0:0]rate_rate_0;
  wire [1:0]\rate_reg1_reg[1] ;
  wire rate_txsync_start;
  wire reg_clock_locked;
  wire reg_clock_locked_reg;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire reset_n_reg1;
  wire reset_n_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire reset_n_reg2;
  wire rst_cpllreset;
  wire rst_drp_start;
  wire rst_drp_x16;
  wire rst_gtreset;
  wire rst_userrdy;
  wire rxeq_adapt_done;
  wire rxsyncallin;
  wire rxusrclk_rst_reg2;
  wire sync_txdlyen;
  wire sys_clk;
  wire txphaligndone0;
  wire txsync_done;
  wire user_eyescanreset;
  wire user_oobclk;
  wire user_resetdone;
  wire user_resetovrd;
  wire user_rxbufreset;
  wire user_rxcdrfreqreset;
  wire user_rxcdrlock;
  wire user_rxcdrreset;
  wire user_rxpcsreset;
  wire user_rxpmareset;

  (* BOX_TYPE = "PRIMITIVE" *) 
  BUFG cpllpd_refclk_inst
       (.I(sys_clk),
        .O(gt_cpllpdrefclk));
  pcie_7x_bridge_gtp_pipe_reset \gtp_pipe_reset.gtp_pipe_reset_i 
       (.\FSM_onehot_fsm_reg[1]_0 (\gtp_pipe_reset.gtp_pipe_reset_i_n_10 ),
        .PLL0RESET0(\qpll_wrapper_i/PLL0RESET0 ),
        .Q({rate_txsync_start,\pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i_n_5 }),
        .SR(dclk_rst_reg2),
        .SYNC_TXSYNC_START0(SYNC_TXSYNC_START0),
        .cpllrst(\qpll_wrapper_i/cpllrst ),
        .done(done),
        .gt_phystatus(gt_phystatus),
        .out(reset_n_reg2),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .plllock_reg1_reg_0(\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_1 ),
        .reset_n_reg2_reg(\gtp_pipe_reset.gtp_pipe_reset_i_n_0 ),
        .rst_cpllreset(rst_cpllreset),
        .rst_drp_start(rst_drp_start),
        .rst_drp_x16(rst_drp_x16),
        .rst_gtreset(rst_gtreset),
        .rst_userrdy(rst_userrdy),
        .\rxpmaresetdone_reg1_reg[0]_0 (\pipe_lane[0].gt_wrapper_i_n_10 ),
        .rxusrclk_rst_reg2_reg_0(rxusrclk_rst_reg2),
        .txsync_done(txsync_done),
        .user_resetdone(user_resetdone),
        .user_rxcdrlock(user_rxcdrlock));
  pcie_7x_bridge_gt_wrapper \pipe_lane[0].gt_wrapper_i 
       (.D({\pipe_lane[0].gt_wrapper_i_n_22 ,\pipe_lane[0].gt_wrapper_i_n_23 ,\pipe_lane[0].gt_wrapper_i_n_24 ,\pipe_lane[0].gt_wrapper_i_n_25 ,\pipe_lane[0].gt_wrapper_i_n_26 ,\pipe_lane[0].gt_wrapper_i_n_27 ,\pipe_lane[0].gt_wrapper_i_n_28 ,\pipe_lane[0].gt_wrapper_i_n_29 ,\pipe_lane[0].gt_wrapper_i_n_30 ,\pipe_lane[0].gt_wrapper_i_n_31 ,\pipe_lane[0].gt_wrapper_i_n_32 ,\pipe_lane[0].gt_wrapper_i_n_33 ,\pipe_lane[0].gt_wrapper_i_n_34 ,\pipe_lane[0].gt_wrapper_i_n_35 ,\pipe_lane[0].gt_wrapper_i_n_36 ,\pipe_lane[0].gt_wrapper_i_n_37 }),
        .DRPADDR(drp_mux_addr),
        .DRPDI(drp_mux_di),
        .PIPE_RXSTATUS(PIPE_RXSTATUS),
        .Q({\pipe_lane[0].pipe_sync_i_n_6 ,\pipe_lane[0].pipe_sync_i_n_7 ,\pipe_lane[0].pipe_sync_i_n_8 }),
        .RXRATE(rate_rate_0),
        .TXMAINCURSOR(eq_txeq_maincursor),
        .TXPOSTCURSOR(eq_txeq_postcursor),
        .TXPRECURSOR(eq_txeq_precursor),
        .drp_mux_en(drp_mux_en),
        .gt_phystatus(gt_phystatus),
        .gt_rx_elec_idle_wire_filter(gt_rx_elec_idle_wire_filter),
        .gt_rxcdrlock(gt_rxcdrlock),
        .gt_rxratedone(gt_rxratedone),
        .gt_rxresetdone(gt_rxresetdone),
        .gt_rxvalid(gt_rxvalid),
        .gt_txratedone(gt_txratedone),
        .gt_txresetdone(gt_txresetdone),
        .gt_txsyncdone(gt_txsyncdone),
        .\gtp_channel.gtpe2_channel_i_0 (\pipe_lane[0].gt_wrapper_i_n_0 ),
        .\gtp_channel.gtpe2_channel_i_1 (\pipe_lane[0].gt_wrapper_i_n_6 ),
        .\gtp_channel.gtpe2_channel_i_10 (\pipe_lane[0].gtp_pipe_drp.gtp_pipe_drp_i_n_1 ),
        .\gtp_channel.gtpe2_channel_i_11 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_2 ),
        .\gtp_channel.gtpe2_channel_i_12 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_3 ),
        .\gtp_channel.gtpe2_channel_i_2 (\pipe_lane[0].gt_wrapper_i_n_9 ),
        .\gtp_channel.gtpe2_channel_i_3 (\pipe_lane[0].gt_wrapper_i_n_10 ),
        .\gtp_channel.gtpe2_channel_i_4 (\pipe_lane[0].gt_wrapper_i_n_13 ),
        .\gtp_channel.gtpe2_channel_i_5 (\pipe_lane[0].gt_wrapper_i_n_15 ),
        .\gtp_channel.gtpe2_channel_i_6 (\pipe_lane[0].gt_wrapper_i_n_17 ),
        .\gtp_channel.gtpe2_channel_i_7 (\pipe_lane[0].gt_wrapper_i_n_18 ),
        .\gtp_channel.gtpe2_channel_i_8 (\gtp_channel.gtpe2_channel_i ),
        .\gtp_channel.gtpe2_channel_i_9 (D),
        .pci_exp_rxn(pci_exp_rxn),
        .pci_exp_rxp(pci_exp_rxp),
        .pci_exp_txn(pci_exp_txn),
        .pci_exp_txp(pci_exp_txp),
        .pipe_dclk_in(pipe_dclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_rx0_chanisaligned(pipe_rx0_chanisaligned),
        .pipe_rx0_polarity(pipe_rx0_polarity),
        .pipe_rxoutclk_out(pipe_rxoutclk_out),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_tx0_char_is_k(pipe_tx0_char_is_k),
        .pipe_tx0_compliance(pipe_tx0_compliance),
        .pipe_tx0_data(pipe_tx0_data),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle),
        .pipe_tx0_powerdown(pipe_tx0_powerdown),
        .pipe_tx_deemph(pipe_tx_deemph),
        .pipe_tx_margin(pipe_tx_margin),
        .pipe_tx_rcvr_det(pipe_tx_rcvr_det),
        .pipe_txoutclk_out(pipe_txoutclk_out),
        .rst_gtreset(rst_gtreset),
        .rst_userrdy(rst_userrdy),
        .rxsyncallin(rxsyncallin),
        .sync_txdlyen(sync_txdlyen),
        .txphaligndone0(txphaligndone0),
        .user_eyescanreset(user_eyescanreset),
        .user_oobclk(user_oobclk),
        .user_resetovrd(user_resetovrd),
        .user_rxbufreset(user_rxbufreset),
        .user_rxcdrfreqreset(user_rxcdrfreqreset),
        .user_rxcdrreset(user_rxcdrreset),
        .user_rxpcsreset(user_rxpcsreset),
        .user_rxpmareset(user_rxpmareset));
  pcie_7x_bridge_gtp_pipe_drp \pipe_lane[0].gtp_pipe_drp.gtp_pipe_drp_i 
       (.D({\pipe_lane[0].gt_wrapper_i_n_22 ,\pipe_lane[0].gt_wrapper_i_n_23 ,\pipe_lane[0].gt_wrapper_i_n_24 ,\pipe_lane[0].gt_wrapper_i_n_25 ,\pipe_lane[0].gt_wrapper_i_n_26 ,\pipe_lane[0].gt_wrapper_i_n_27 ,\pipe_lane[0].gt_wrapper_i_n_28 ,\pipe_lane[0].gt_wrapper_i_n_29 ,\pipe_lane[0].gt_wrapper_i_n_30 ,\pipe_lane[0].gt_wrapper_i_n_31 ,\pipe_lane[0].gt_wrapper_i_n_32 ,\pipe_lane[0].gt_wrapper_i_n_33 ,\pipe_lane[0].gt_wrapper_i_n_34 ,\pipe_lane[0].gt_wrapper_i_n_35 ,\pipe_lane[0].gt_wrapper_i_n_36 ,\pipe_lane[0].gt_wrapper_i_n_37 }),
        .DRPADDR(drp_mux_addr),
        .DRPDI(drp_mux_di),
        .DRP_START0(DRP_START0),
        .DRP_X160(DRP_X160),
        .SR(dclk_rst_reg2),
        .done(done),
        .drp_mux_en(drp_mux_en),
        .\fsm_reg[1]_0 (\pipe_lane[0].gtp_pipe_drp.gtp_pipe_drp_i_n_1 ),
        .pipe_dclk_in(pipe_dclk_in),
        .rdy_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_0 ));
  pcie_7x_bridge_gtp_pipe_rate \pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i 
       (.DRP_START0(DRP_START0),
        .DRP_X160(DRP_X160),
        .Q({rate_txsync_start,rate_done,\pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i_n_5 }),
        .RXRATE(rate_rate_0),
        .done(done),
        .gt_phystatus(gt_phystatus),
        .gt_rxratedone(gt_rxratedone),
        .gt_txratedone(gt_txratedone),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .\rate_in_reg1_reg[1]_0 (\rate_in_reg1_reg[1] ),
        .rst_cpllreset(rst_cpllreset),
        .rst_drp_start(rst_drp_start),
        .rst_drp_x16(rst_drp_x16),
        .rxpmaresetdone_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_10 ),
        .txsync_done(txsync_done));
  pcie_7x_bridge_pipe_eq \pipe_lane[0].pipe_eq.pipe_eq_i 
       (.TXMAINCURSOR(eq_txeq_maincursor),
        .TXPOSTCURSOR(eq_txeq_postcursor),
        .TXPRECURSOR(eq_txeq_precursor),
        .pipe_pclk_in(pipe_pclk_in),
        .rst_cpllreset(rst_cpllreset),
        .rxeq_adapt_done(rxeq_adapt_done));
  pcie_7x_bridge_gt_common \pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i 
       (.PLL0RESET0(\qpll_wrapper_i/PLL0RESET0 ),
        .Q(qrst_drp_start),
        .SR(dclk_rst_reg2),
        .cpllrst(\qpll_wrapper_i/cpllrst ),
        .done_reg(\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_4 ),
        .gt_cpllpdrefclk(gt_cpllpdrefclk),
        .\gtp_common.gtpe2_common_i (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_1 ),
        .\gtp_common.gtpe2_common_i_0 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_2 ),
        .\gtp_common.gtpe2_common_i_1 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_3 ),
        .pipe_dclk_in(pipe_dclk_in),
        .sys_clk(sys_clk));
  pcie_7x_bridge_pipe_sync \pipe_lane[0].pipe_sync_i 
       (.\FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 (\pipe_lane[0].pipe_user_i_n_15 ),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 ({\pipe_lane[0].pipe_sync_i_n_6 ,\pipe_lane[0].pipe_sync_i_n_7 ,\pipe_lane[0].pipe_sync_i_n_8 }),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_1 (\pipe_lane[0].pipe_user_i_n_16 ),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_2 (\pipe_lane[0].pipe_user_i_n_20 ),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[6]_0 (p_0_in4_in),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[6]_1 (p_1_in5_in),
        .Q(\pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i_n_5 ),
        .SYNC_TXPHINITDONE1(SYNC_TXPHINITDONE1),
        .SYNC_TXSYNC_START0(SYNC_TXSYNC_START0),
        .gt_rx_elec_idle_wire_filter(gt_rx_elec_idle_wire_filter),
        .gt_txsyncdone(gt_txsyncdone),
        .out(p_1_in),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_pclk_in(pipe_pclk_in),
        .rst_cpllreset(rst_cpllreset),
        .rxdlysresetdone_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_6 ),
        .rxphaligndone_m_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_9 ),
        .rxsyncdone_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_13 ),
        .sync_txdlyen(sync_txdlyen),
        .txdlysresetdone_reg1_reg_0(\pipe_lane[0].gt_wrapper_i_n_15 ),
        .txphaligndone0(txphaligndone0),
        .txphaligndone_reg3_reg_0(\pipe_lane[0].pipe_sync_i_n_1 ),
        .txphinitdone_reg2_reg_0(p_1_in0_in),
        .txphinitdone_reg3_reg_0(\pipe_lane[0].pipe_sync_i_n_3 ),
        .txsync_done(txsync_done),
        .user_rxcdrlock(user_rxcdrlock));
  pcie_7x_bridge_pipe_user \pipe_lane[0].pipe_user_i 
       (.\FSM_onehot_txsync_fsm.fsm_tx_reg[4] (\pipe_lane[0].pipe_sync_i_n_3 ),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[4]_0 (p_1_in0_in),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[5] (\pipe_lane[0].pipe_sync_i_n_1 ),
        .\FSM_onehot_txsync_fsm.fsm_tx_reg[5]_0 (p_1_in),
        .PIPE_RXSTATUS(PIPE_RXSTATUS[2]),
        .Q({rate_done,\pipe_lane[0].gtp_pipe_rate.gtp_pipe_rate_i_n_5 }),
        .SR(rxusrclk_rst_reg2),
        .SYNC_TXPHINITDONE1(SYNC_TXPHINITDONE1),
        .gt_phystatus(gt_phystatus),
        .gt_rx_elec_idle_wire_filter(gt_rx_elec_idle_wire_filter),
        .gt_rx_phy_status_wire_filter(gt_rx_phy_status_wire_filter),
        .gt_rxcdrlock(gt_rxcdrlock),
        .gt_rxresetdone(gt_rxresetdone),
        .gt_rxvalid(gt_rxvalid),
        .gt_rxvalid_q12_out(gt_rxvalid_q12_out),
        .gt_rxvalid_q_reg(gt_rxvalid_q_reg),
        .gt_txresetdone(gt_txresetdone),
        .\gtp_channel.gtpe2_channel_i (\pipe_lane[0].gt_wrapper_i_n_9 ),
        .out(p_1_in5_in),
        .pipe_oobclk_in(pipe_oobclk_in),
        .pipe_pclk_in(pipe_pclk_in),
        .pipe_pclk_sel_out(pipe_pclk_sel_out),
        .pipe_rx0_valid(pipe_rx0_valid),
        .pipe_rxusrclk_in(pipe_rxusrclk_in),
        .pipe_tx0_compliance(pipe_tx0_compliance),
        .pipe_tx0_elec_idle(pipe_tx0_elec_idle),
        .plm_in_l0__4(plm_in_l0__4),
        .reg_clock_locked(reg_clock_locked),
        .reg_clock_locked_reg(reg_clock_locked_reg),
        .rst_cpllreset(rst_cpllreset),
        .rst_idle_reg1_reg_0(\gtp_pipe_reset.gtp_pipe_reset_i_n_10 ),
        .rxeq_adapt_done(rxeq_adapt_done),
        .rxsyncallin(rxsyncallin),
        .txcompliance_reg2_reg_0(p_0_in4_in),
        .txcompliance_reg2_reg_1(\pipe_lane[0].pipe_user_i_n_15 ),
        .txcompliance_reg2_reg_2(\pipe_lane[0].pipe_user_i_n_16 ),
        .txelecidle_reg2_reg_0(\pipe_lane[0].pipe_user_i_n_20 ),
        .txphaligndone0(txphaligndone0),
        .txphaligndone_reg1_reg(\pipe_lane[0].gt_wrapper_i_n_17 ),
        .txphinitdone_reg1_reg(\pipe_lane[0].gt_wrapper_i_n_18 ),
        .user_eyescanreset(user_eyescanreset),
        .user_oobclk(user_oobclk),
        .user_resetdone(user_resetdone),
        .user_resetovrd(user_resetovrd),
        .user_rxbufreset(user_rxbufreset),
        .user_rxcdrfreqreset(user_rxcdrfreqreset),
        .user_rxcdrlock(user_rxcdrlock),
        .user_rxcdrreset(user_rxcdrreset),
        .user_rxpcsreset(user_rxpcsreset),
        .user_rxpmareset(user_rxpmareset));
  LUT1 #(
    .INIT(2'h1)) 
    pl_phy_lnk_up_q_i_1
       (.I0(reset_n_reg1_reg_0),
        .O(p_0_in_0));
  pcie_7x_bridge_qpll_reset \qpll_reset.qpll_reset_i 
       (.Q(qrst_drp_start),
        .\drp_done_reg1_reg[0]_0 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_4 ),
        .mmcm_lock_reg1_reg_0(\gtp_pipe_reset.gtp_pipe_reset_i_n_0 ),
        .pipe_mmcm_lock_in(pipe_mmcm_lock_in),
        .pipe_pclk_in(pipe_pclk_in),
        .\qplllock_reg1_reg[0]_0 (\pipe_lane[0].pipe_quad.gt_common_enabled.gt_common_int.gt_common_i_n_1 ),
        .\rate_reg1_reg[1]_0 (\rate_reg1_reg[1] ));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDCE reset_n_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(p_0_in_0),
        .D(1'b1),
        .Q(reset_n_reg1));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDCE reset_n_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .CLR(p_0_in_0),
        .D(reset_n_reg1),
        .Q(reset_n_reg2));
endmodule

module pcie_7x_bridge_qpll_drp
   (done_reg_0,
    \addr_reg[7]_0 ,
    \di_reg[15]_0 ,
    qpll_drp_en,
    qpll_drp_we,
    SR,
    pipe_dclk_in,
    Q,
    qpll_drp_rdy,
    qplllock_reg1_reg_0,
    D);
  output done_reg_0;
  output [4:0]\addr_reg[7]_0 ;
  output [15:0]\di_reg[15]_0 ;
  output qpll_drp_en;
  output qpll_drp_we;
  input [0:0]SR;
  input pipe_dclk_in;
  input [0:0]Q;
  input qpll_drp_rdy;
  input qplllock_reg1_reg_0;
  input [15:0]D;

  wire [15:0]D;
  wire [0:0]Q;
  wire [0:0]SR;
  wire \addr[0]_i_1_n_0 ;
  wire \addr[1]_i_1_n_0 ;
  wire \addr[2]_i_1_n_0 ;
  wire \addr[5]_i_1_n_0 ;
  wire \addr[7]_i_1_n_0 ;
  wire [4:0]\addr_reg[7]_0 ;
  wire [5:0]crscode;
  wire \crscode[0]_i_1_n_0 ;
  wire \crscode[1]_i_1_n_0 ;
  wire \crscode[2]_i_1_n_0 ;
  wire \crscode[3]_i_1_n_0 ;
  wire \crscode[4]_i_1_n_0 ;
  wire \crscode[5]_i_1_n_0 ;
  wire \crscode[5]_i_2_n_0 ;
  wire [15:0]di;
  wire \di[11]_i_2_n_0 ;
  wire \di[12]_i_2_n_0 ;
  wire \di[13]_i_2_n_0 ;
  wire \di[14]_i_2_n_0 ;
  wire \di[15]_i_2_n_0 ;
  wire [15:0]\di_reg[15]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [15:0]do_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [15:0]do_reg2;
  wire done;
  wire done_reg_0;
  wire \fsm[1]_i_2_n_0 ;
  wire \fsm[1]_i_3_n_0 ;
  wire \fsm_inferred__1/i___0_n_0 ;
  wire \fsm_inferred__1/i___1_n_0 ;
  wire \fsm_inferred__1/i__n_0 ;
  wire \fsm_reg_n_0_[0] ;
  wire \fsm_reg_n_0_[1] ;
  wire \fsm_reg_n_0_[2] ;
  wire \fsm_reg_n_0_[3] ;
  wire \fsm_reg_n_0_[4] ;
  wire \fsm_reg_n_0_[5] ;
  wire \fsm_reg_n_0_[6] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire gen3_reg2;
  wire \gtp_common.gtpe2_common_i_i_4_n_0 ;
  wire \gtp_common.gtpe2_common_i_i_5_n_0 ;
  wire index;
  wire \index[0]_i_1_n_0 ;
  wire \index[0]_i_2_n_0 ;
  wire \index[1]_i_1_n_0 ;
  wire \index[2]_i_1_n_0 ;
  wire \index[2]_i_2_n_0 ;
  wire \index[2]_i_3_n_0 ;
  wire \index[2]_i_5_n_0 ;
  wire \index_reg_n_0_[0] ;
  wire \index_reg_n_0_[1] ;
  wire \index_reg_n_0_[2] ;
  wire [1:0]load_cnt;
  wire \load_cnt[0]_i_1__0_n_0 ;
  wire \load_cnt[1]_i_1_n_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire ovrd_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire ovrd_reg2;
  wire [6:0]p_0_in__0;
  wire pipe_dclk_in;
  wire qpll_drp_en;
  wire qpll_drp_rdy;
  wire qpll_drp_we;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qplllock_reg1;
  wire qplllock_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qplllock_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rdy_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire rdy_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire start_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire start_reg2;

  (* SOFT_HLUTNM = "soft_lutpair49" *) 
  LUT3 #(
    .INIT(8'h06)) 
    \addr[0]_i_1 
       (.I0(\index_reg_n_0_[2] ),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[0] ),
        .O(\addr[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair48" *) 
  LUT3 #(
    .INIT(8'h0D)) 
    \addr[1]_i_1 
       (.I0(\index_reg_n_0_[2] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[1] ),
        .O(\addr[1]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair47" *) 
  LUT3 #(
    .INIT(8'h4D)) 
    \addr[2]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[2] ),
        .I2(\index_reg_n_0_[0] ),
        .O(\addr[2]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h7)) 
    \addr[5]_i_1 
       (.I0(\index_reg_n_0_[0] ),
        .I1(\index_reg_n_0_[1] ),
        .O(\addr[5]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair48" *) 
  LUT3 #(
    .INIT(8'h08)) 
    \addr[7]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .O(\addr[7]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\addr[0]_i_1_n_0 ),
        .Q(\addr_reg[7]_0 [0]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\addr[1]_i_1_n_0 ),
        .Q(\addr_reg[7]_0 [1]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\addr[2]_i_1_n_0 ),
        .Q(\addr_reg[7]_0 [2]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\addr[5]_i_1_n_0 ),
        .Q(\addr_reg[7]_0 [3]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \addr_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\addr[7]_i_1_n_0 ),
        .Q(\addr_reg[7]_0 [4]),
        .R(SR));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[0]_i_1 
       (.I0(do_reg2[1]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[0]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[1]_i_1 
       (.I0(do_reg2[2]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[1]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[2]_i_1 
       (.I0(do_reg2[3]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[2]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[3]_i_1 
       (.I0(do_reg2[4]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[3]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[4]_i_1 
       (.I0(do_reg2[5]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[4]_i_1_n_0 ));
  LUT4 #(
    .INIT(16'hC080)) 
    \crscode[5]_i_1 
       (.I0(ovrd_reg2),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[1] ),
        .I3(\index_reg_n_0_[2] ),
        .O(\crscode[5]_i_1_n_0 ));
  LUT2 #(
    .INIT(4'h2)) 
    \crscode[5]_i_2 
       (.I0(do_reg2[6]),
        .I1(\index_reg_n_0_[2] ),
        .O(\crscode[5]_i_2_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[0] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[0]_i_1_n_0 ),
        .Q(crscode[0]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[1] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[1]_i_1_n_0 ),
        .Q(crscode[1]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[2] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[2]_i_1_n_0 ),
        .Q(crscode[2]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[3] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[3]_i_1_n_0 ),
        .Q(crscode[3]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[4] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[4]_i_1_n_0 ),
        .Q(crscode[4]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \crscode_reg[5] 
       (.C(pipe_dclk_in),
        .CE(\crscode[5]_i_1_n_0 ),
        .D(\crscode[5]_i_2_n_0 ),
        .Q(crscode[5]),
        .R(SR));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[0]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[0]),
        .O(di[0]));
  LUT5 #(
    .INIT(32'h0CC5CCCC)) 
    \di[10]_i_1 
       (.I0(crscode[0]),
        .I1(do_reg2[10]),
        .I2(\index_reg_n_0_[1] ),
        .I3(\index_reg_n_0_[0] ),
        .I4(\index_reg_n_0_[2] ),
        .O(di[10]));
  LUT6 #(
    .INIT(64'hFFFFFFFF00000090)) 
    \di[11]_i_1 
       (.I0(crscode[0]),
        .I1(crscode[1]),
        .I2(\index_reg_n_0_[2] ),
        .I3(\index_reg_n_0_[0] ),
        .I4(\index_reg_n_0_[1] ),
        .I5(\di[11]_i_2_n_0 ),
        .O(di[11]));
  LUT5 #(
    .INIT(32'h40FF4022)) 
    \di[11]_i_2 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(ovrd_reg2),
        .I3(\index_reg_n_0_[2] ),
        .I4(do_reg2[11]),
        .O(\di[11]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h00AA00AAAAAAC3AA)) 
    \di[12]_i_1 
       (.I0(do_reg2[12]),
        .I1(\di[12]_i_2_n_0 ),
        .I2(crscode[2]),
        .I3(\index_reg_n_0_[2] ),
        .I4(\index_reg_n_0_[0] ),
        .I5(\index_reg_n_0_[1] ),
        .O(di[12]));
  LUT2 #(
    .INIT(4'hE)) 
    \di[12]_i_2 
       (.I0(crscode[0]),
        .I1(crscode[1]),
        .O(\di[12]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h00AAAAFFAAAAC3AA)) 
    \di[13]_i_1 
       (.I0(do_reg2[13]),
        .I1(\di[13]_i_2_n_0 ),
        .I2(crscode[3]),
        .I3(\index_reg_n_0_[2] ),
        .I4(\index_reg_n_0_[0] ),
        .I5(\index_reg_n_0_[1] ),
        .O(di[13]));
  (* SOFT_HLUTNM = "soft_lutpair44" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    \di[13]_i_2 
       (.I0(crscode[1]),
        .I1(crscode[0]),
        .I2(crscode[2]),
        .O(\di[13]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h0AAFAA3A)) 
    \di[14]_i_1 
       (.I0(do_reg2[14]),
        .I1(\di[14]_i_2_n_0 ),
        .I2(\index_reg_n_0_[2] ),
        .I3(\index_reg_n_0_[0] ),
        .I4(\index_reg_n_0_[1] ),
        .O(di[14]));
  (* SOFT_HLUTNM = "soft_lutpair44" *) 
  LUT5 #(
    .INIT(32'h0001FFFE)) 
    \di[14]_i_2 
       (.I0(crscode[3]),
        .I1(crscode[1]),
        .I2(crscode[0]),
        .I3(crscode[2]),
        .I4(crscode[4]),
        .O(\di[14]_i_2_n_0 ));
  LUT5 #(
    .INIT(32'h0CC5CCCC)) 
    \di[15]_i_1 
       (.I0(\di[15]_i_2_n_0 ),
        .I1(do_reg2[15]),
        .I2(\index_reg_n_0_[1] ),
        .I3(\index_reg_n_0_[0] ),
        .I4(\index_reg_n_0_[2] ),
        .O(di[15]));
  LUT6 #(
    .INIT(64'h00000001FFFFFFFE)) 
    \di[15]_i_2 
       (.I0(crscode[1]),
        .I1(crscode[0]),
        .I2(crscode[2]),
        .I3(crscode[3]),
        .I4(crscode[4]),
        .I5(crscode[5]),
        .O(\di[15]_i_2_n_0 ));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[1]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[1]),
        .O(di[1]));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[2]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[2]),
        .O(di[2]));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[3]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[3]),
        .O(di[3]));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[4]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[4]),
        .O(di[4]));
  LUT4 #(
    .INIT(16'h2AAB)) 
    \di[5]_i_1 
       (.I0(do_reg2[5]),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[0] ),
        .I3(\index_reg_n_0_[2] ),
        .O(di[5]));
  LUT4 #(
    .INIT(16'h2BA8)) 
    \di[6]_i_1 
       (.I0(do_reg2[6]),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(\index_reg_n_0_[0] ),
        .O(di[6]));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[7]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[7]),
        .O(di[7]));
  LUT4 #(
    .INIT(16'h2AAB)) 
    \di[8]_i_1 
       (.I0(do_reg2[8]),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[0] ),
        .I3(\index_reg_n_0_[2] ),
        .O(di[8]));
  LUT4 #(
    .INIT(16'h7E00)) 
    \di[9]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index_reg_n_0_[2] ),
        .I3(do_reg2[9]),
        .O(di[9]));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[0]),
        .Q(\di_reg[15]_0 [0]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[10]),
        .Q(\di_reg[15]_0 [10]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[11]),
        .Q(\di_reg[15]_0 [11]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[12]),
        .Q(\di_reg[15]_0 [12]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[13]),
        .Q(\di_reg[15]_0 [13]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[14]),
        .Q(\di_reg[15]_0 [14]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[15]),
        .Q(\di_reg[15]_0 [15]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[1]),
        .Q(\di_reg[15]_0 [1]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[2]),
        .Q(\di_reg[15]_0 [2]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[3]),
        .Q(\di_reg[15]_0 [3]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[4]),
        .Q(\di_reg[15]_0 [4]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[5]),
        .Q(\di_reg[15]_0 [5]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[6]),
        .Q(\di_reg[15]_0 [6]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[7]),
        .Q(\di_reg[15]_0 [7]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[8]),
        .Q(\di_reg[15]_0 [8]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \di_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(di[9]),
        .Q(\di_reg[15]_0 [9]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[0]),
        .Q(do_reg1[0]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[10]),
        .Q(do_reg1[10]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[11]),
        .Q(do_reg1[11]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[12]),
        .Q(do_reg1[12]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[13]),
        .Q(do_reg1[13]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[14]),
        .Q(do_reg1[14]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[15]),
        .Q(do_reg1[15]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[1]),
        .Q(do_reg1[1]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[2]),
        .Q(do_reg1[2]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[3]),
        .Q(do_reg1[3]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[4]),
        .Q(do_reg1[4]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[5]),
        .Q(do_reg1[5]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[6]),
        .Q(do_reg1[6]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[7]),
        .Q(do_reg1[7]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[8]),
        .Q(do_reg1[8]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg1_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(D[9]),
        .Q(do_reg1[9]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[0]),
        .Q(do_reg2[0]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[10] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[10]),
        .Q(do_reg2[10]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[11] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[11]),
        .Q(do_reg2[11]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[12] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[12]),
        .Q(do_reg2[12]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[13] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[13]),
        .Q(do_reg2[13]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[14] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[14]),
        .Q(do_reg2[14]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[15] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[15]),
        .Q(do_reg2[15]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[1]),
        .Q(do_reg2[1]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[2]),
        .Q(do_reg2[2]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[3]),
        .Q(do_reg2[3]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[4]),
        .Q(do_reg2[4]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[5]),
        .Q(do_reg2[5]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[6]),
        .Q(do_reg2[6]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[7] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[7]),
        .Q(do_reg2[7]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[8] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[8]),
        .Q(do_reg2[8]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \do_reg2_reg[9] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(do_reg1[9]),
        .Q(do_reg2[9]),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000000000010000)) 
    done_i_1__0
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\fsm_reg_n_0_[6] ),
        .I2(start_reg2),
        .I3(\fsm_reg_n_0_[4] ),
        .I4(\fsm_reg_n_0_[0] ),
        .I5(\gtp_common.gtpe2_common_i_i_5_n_0 ),
        .O(done));
  FDRE #(
    .INIT(1'b0)) 
    done_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(done),
        .Q(done_reg_0),
        .R(SR));
  LUT5 #(
    .INIT(32'h5DFF5D5D)) 
    \fsm[0]_i_1__0 
       (.I0(\fsm_inferred__1/i___1_n_0 ),
        .I1(\fsm_reg_n_0_[0] ),
        .I2(start_reg2),
        .I3(\fsm[1]_i_3_n_0 ),
        .I4(\fsm_reg_n_0_[6] ),
        .O(p_0_in__0[0]));
  LUT6 #(
    .INIT(64'hFFAAEAAAEAAAEAAA)) 
    \fsm[1]_i_1__0 
       (.I0(\fsm[1]_i_2_n_0 ),
        .I1(start_reg2),
        .I2(\fsm_reg_n_0_[0] ),
        .I3(\fsm_inferred__1/i___1_n_0 ),
        .I4(\fsm_reg_n_0_[6] ),
        .I5(\fsm[1]_i_3_n_0 ),
        .O(p_0_in__0[1]));
  (* SOFT_HLUTNM = "soft_lutpair46" *) 
  LUT4 #(
    .INIT(16'h0888)) 
    \fsm[1]_i_2 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\fsm_inferred__1/i___1_n_0 ),
        .I2(load_cnt[1]),
        .I3(load_cnt[0]),
        .O(\fsm[1]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair47" *) 
  LUT3 #(
    .INIT(8'hF7)) 
    \fsm[1]_i_3 
       (.I0(\index_reg_n_0_[2] ),
        .I1(\index_reg_n_0_[1] ),
        .I2(\index_reg_n_0_[0] ),
        .O(\fsm[1]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair46" *) 
  LUT4 #(
    .INIT(16'h8000)) 
    \fsm[2]_i_1__0 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\fsm_inferred__1/i___1_n_0 ),
        .I2(load_cnt[1]),
        .I3(load_cnt[0]),
        .O(p_0_in__0[2]));
  LUT4 #(
    .INIT(16'h88C8)) 
    \fsm[3]_i_1 
       (.I0(\fsm_reg_n_0_[2] ),
        .I1(\fsm_inferred__1/i___1_n_0 ),
        .I2(\fsm_reg_n_0_[3] ),
        .I3(rdy_reg2),
        .O(p_0_in__0[3]));
  LUT3 #(
    .INIT(8'h80)) 
    \fsm[4]_i_1 
       (.I0(rdy_reg2),
        .I1(\fsm_reg_n_0_[3] ),
        .I2(\fsm_inferred__1/i___1_n_0 ),
        .O(p_0_in__0[4]));
  LUT4 #(
    .INIT(16'h88C8)) 
    \fsm[5]_i_1 
       (.I0(\fsm_reg_n_0_[4] ),
        .I1(\fsm_inferred__1/i___1_n_0 ),
        .I2(\fsm_reg_n_0_[5] ),
        .I3(rdy_reg2),
        .O(p_0_in__0[5]));
  LUT3 #(
    .INIT(8'h80)) 
    \fsm[6]_i_1 
       (.I0(rdy_reg2),
        .I1(\fsm_reg_n_0_[5] ),
        .I2(\fsm_inferred__1/i___1_n_0 ),
        .O(p_0_in__0[6]));
  (* SOFT_HLUTNM = "soft_lutpair45" *) 
  LUT4 #(
    .INIT(16'h0116)) 
    \fsm_inferred__1/i_ 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[2] ),
        .I3(\fsm_reg_n_0_[3] ),
        .O(\fsm_inferred__1/i__n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair45" *) 
  LUT4 #(
    .INIT(16'hFEE8)) 
    \fsm_inferred__1/i___0 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[2] ),
        .I3(\fsm_reg_n_0_[3] ),
        .O(\fsm_inferred__1/i___0_n_0 ));
  LUT5 #(
    .INIT(32'h00000116)) 
    \fsm_inferred__1/i___1 
       (.I0(\fsm_reg_n_0_[4] ),
        .I1(\fsm_reg_n_0_[5] ),
        .I2(\fsm_reg_n_0_[6] ),
        .I3(\fsm_inferred__1/i__n_0 ),
        .I4(\fsm_inferred__1/i___0_n_0 ),
        .O(\fsm_inferred__1/i___1_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDSE #(
    .INIT(1'b1)) 
    \fsm_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[0]),
        .Q(\fsm_reg_n_0_[0] ),
        .S(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[1]),
        .Q(\fsm_reg_n_0_[1] ),
        .R(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[2]),
        .Q(\fsm_reg_n_0_[2] ),
        .R(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[3] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[3]),
        .Q(\fsm_reg_n_0_[3] ),
        .R(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[4] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[4]),
        .Q(\fsm_reg_n_0_[4] ),
        .R(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[5] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[5]),
        .Q(\fsm_reg_n_0_[5] ),
        .R(SR));
  (* FSM_ENCODED_STATES = "FSM_READ:000000100,FSM_QPLLRESET:010000000,FSM_LOAD:000000010,FSM_DONE:001000000,FSM_WRITE:000010000,FSM_IDLE:000000001,FSM_WRDY:000100000,FSM_RRDY:000001000,FSM_QPLLLOCK:100000000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \fsm_reg[6] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(p_0_in__0[6]),
        .Q(\fsm_reg_n_0_[6] ),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(gen3_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE gen3_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(gen3_reg1),
        .Q(gen3_reg2),
        .R(SR));
  LUT6 #(
    .INIT(64'h0000000000000014)) 
    \gtp_common.gtpe2_common_i_i_1 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[2] ),
        .I2(\fsm_reg_n_0_[4] ),
        .I3(\fsm_reg_n_0_[6] ),
        .I4(\fsm_reg_n_0_[1] ),
        .I5(\gtp_common.gtpe2_common_i_i_4_n_0 ),
        .O(qpll_drp_en));
  (* SOFT_HLUTNM = "soft_lutpair41" *) 
  LUT5 #(
    .INIT(32'h00000002)) 
    \gtp_common.gtpe2_common_i_i_2 
       (.I0(\fsm_reg_n_0_[4] ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[6] ),
        .I3(\fsm_reg_n_0_[0] ),
        .I4(\gtp_common.gtpe2_common_i_i_5_n_0 ),
        .O(qpll_drp_we));
  LUT2 #(
    .INIT(4'hE)) 
    \gtp_common.gtpe2_common_i_i_4 
       (.I0(\fsm_reg_n_0_[3] ),
        .I1(\fsm_reg_n_0_[5] ),
        .O(\gtp_common.gtpe2_common_i_i_4_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair43" *) 
  LUT3 #(
    .INIT(8'hFE)) 
    \gtp_common.gtpe2_common_i_i_5 
       (.I0(\fsm_reg_n_0_[5] ),
        .I1(\fsm_reg_n_0_[3] ),
        .I2(\fsm_reg_n_0_[2] ),
        .O(\gtp_common.gtpe2_common_i_i_5_n_0 ));
  LUT6 #(
    .INIT(64'h0000FFFF20000000)) 
    \index[0]_i_1 
       (.I0(\index[0]_i_2_n_0 ),
        .I1(\fsm_reg_n_0_[1] ),
        .I2(\fsm_reg_n_0_[6] ),
        .I3(\index[2]_i_3_n_0 ),
        .I4(index),
        .I5(\index_reg_n_0_[0] ),
        .O(\index[0]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair49" *) 
  LUT2 #(
    .INIT(4'h7)) 
    \index[0]_i_2 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[2] ),
        .O(\index[0]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h1000FFFFC0000000)) 
    \index[1]_i_1 
       (.I0(\index_reg_n_0_[2] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index[2]_i_2_n_0 ),
        .I3(\index[2]_i_3_n_0 ),
        .I4(index),
        .I5(\index_reg_n_0_[1] ),
        .O(\index[1]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h5000FFFF80000000)) 
    \index[2]_i_1 
       (.I0(\index_reg_n_0_[1] ),
        .I1(\index_reg_n_0_[0] ),
        .I2(\index[2]_i_2_n_0 ),
        .I3(\index[2]_i_3_n_0 ),
        .I4(index),
        .I5(\index_reg_n_0_[2] ),
        .O(\index[2]_i_1_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair41" *) 
  LUT2 #(
    .INIT(4'h2)) 
    \index[2]_i_2 
       (.I0(\fsm_reg_n_0_[6] ),
        .I1(\fsm_reg_n_0_[1] ),
        .O(\index[2]_i_2_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair43" *) 
  LUT5 #(
    .INIT(32'h00000001)) 
    \index[2]_i_3 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[5] ),
        .I2(\fsm_reg_n_0_[3] ),
        .I3(\fsm_reg_n_0_[2] ),
        .I4(\fsm_reg_n_0_[4] ),
        .O(\index[2]_i_3_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFEFFFEFEED)) 
    \index[2]_i_4 
       (.I0(\fsm_reg_n_0_[1] ),
        .I1(\index[2]_i_5_n_0 ),
        .I2(\fsm_reg_n_0_[2] ),
        .I3(\fsm_reg_n_0_[3] ),
        .I4(\fsm_reg_n_0_[5] ),
        .I5(\fsm_reg_n_0_[4] ),
        .O(index));
  LUT2 #(
    .INIT(4'hE)) 
    \index[2]_i_5 
       (.I0(\fsm_reg_n_0_[0] ),
        .I1(\fsm_reg_n_0_[6] ),
        .O(\index[2]_i_5_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\index[0]_i_1_n_0 ),
        .Q(\index_reg_n_0_[0] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\index[1]_i_1_n_0 ),
        .Q(\index_reg_n_0_[1] ),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \index_reg[2] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\index[2]_i_1_n_0 ),
        .Q(\index_reg_n_0_[2] ),
        .R(SR));
  (* SOFT_HLUTNM = "soft_lutpair42" *) 
  LUT5 #(
    .INIT(32'h00B00000)) 
    \load_cnt[0]_i_1__0 
       (.I0(load_cnt[1]),
        .I1(load_cnt[0]),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[6] ),
        .I4(\index[2]_i_3_n_0 ),
        .O(\load_cnt[0]_i_1__0_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair42" *) 
  LUT5 #(
    .INIT(32'h00E00000)) 
    \load_cnt[1]_i_1 
       (.I0(load_cnt[1]),
        .I1(load_cnt[0]),
        .I2(\fsm_reg_n_0_[1] ),
        .I3(\fsm_reg_n_0_[6] ),
        .I4(\index[2]_i_3_n_0 ),
        .O(\load_cnt[1]_i_1_n_0 ));
  FDRE #(
    .INIT(1'b0)) 
    \load_cnt_reg[0] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\load_cnt[0]_i_1__0_n_0 ),
        .Q(load_cnt[0]),
        .R(SR));
  FDRE #(
    .INIT(1'b0)) 
    \load_cnt_reg[1] 
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(\load_cnt[1]_i_1_n_0 ),
        .Q(load_cnt[1]),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE ovrd_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(ovrd_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE ovrd_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(ovrd_reg1),
        .Q(ovrd_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE qplllock_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(qplllock_reg1_reg_0),
        .Q(qplllock_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE qplllock_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(qplllock_reg1),
        .Q(qplllock_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rdy_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(qpll_drp_rdy),
        .Q(rdy_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE rdy_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(rdy_reg1),
        .Q(rdy_reg2),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE start_reg1_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(Q),
        .Q(start_reg1),
        .R(SR));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE start_reg2_reg
       (.C(pipe_dclk_in),
        .CE(1'b1),
        .D(start_reg1),
        .Q(start_reg2),
        .R(SR));
endmodule

module pcie_7x_bridge_qpll_reset
   (Q,
    mmcm_lock_reg1_reg_0,
    pipe_pclk_in,
    \drp_done_reg1_reg[0]_0 ,
    \qplllock_reg1_reg[0]_0 ,
    pipe_mmcm_lock_in,
    \rate_reg1_reg[1]_0 );
  output [0:0]Q;
  input mmcm_lock_reg1_reg_0;
  input pipe_pclk_in;
  input \drp_done_reg1_reg[0]_0 ;
  input \qplllock_reg1_reg[0]_0 ;
  input pipe_mmcm_lock_in;
  input [1:0]\rate_reg1_reg[1]_0 ;

  wire \FSM_onehot_fsm[0]_i_1__1_n_0 ;
  wire \FSM_onehot_fsm[1]_i_1_n_0 ;
  wire \FSM_onehot_fsm[2]_i_1_n_0 ;
  wire \FSM_onehot_fsm_reg_n_0_[0] ;
  wire \FSM_onehot_fsm_reg_n_0_[1] ;
  wire [0:0]Q;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire cplllock_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire cplllock_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg1;
  wire \drp_done_reg1_reg[0]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire drp_done_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg1;
  wire mmcm_lock_reg1_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire mmcm_lock_reg2;
  wire pipe_mmcm_lock_in;
  wire pipe_pclk_in;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qplllock_reg1;
  wire \qplllock_reg1_reg[0]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qplllock_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qpllpd_in_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qpllpd_in_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qpllreset_in_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire qpllreset_in_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rate_reg1;
  wire [1:0]\rate_reg1_reg[1]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [1:0]rate_reg2;

  LUT3 #(
    .INIT(8'hA8)) 
    \FSM_onehot_fsm[0]_i_1__1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[0] ),
        .I1(qplllock_reg2),
        .I2(cplllock_reg2),
        .O(\FSM_onehot_fsm[0]_i_1__1_n_0 ));
  LUT5 #(
    .INIT(32'h0FFF0044)) 
    \FSM_onehot_fsm[1]_i_1 
       (.I0(qplllock_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[0] ),
        .I2(mmcm_lock_reg2),
        .I3(cplllock_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[1] ),
        .O(\FSM_onehot_fsm[1]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFF808080)) 
    \FSM_onehot_fsm[2]_i_1 
       (.I0(mmcm_lock_reg2),
        .I1(cplllock_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[1] ),
        .I3(drp_done_reg2),
        .I4(Q),
        .O(\FSM_onehot_fsm[2]_i_1_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:00000010,FSM_DRP_START_NOM:00000100,FSM_WAIT_LOCK:00000001,FSM_QPLL_PD:01000000,FSM_QPLL_PDRESET:00100000,FSM_QPLLLOCK2:1010,FSM_IDLE:10000000,FSM_DRP_START_OPT:0111,FSM_QPLL_RESET:1001,FSM_QPLLLOCK:00010000,FSM_DRP_DONE_OPT:1000,FSM_DRP_DONE_NOM:00001000" *) 
  FDSE #(
    .INIT(1'b1)) 
    \FSM_onehot_fsm_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[0]_i_1__1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[0] ),
        .S(mmcm_lock_reg1_reg_0));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:00000010,FSM_DRP_START_NOM:00000100,FSM_WAIT_LOCK:00000001,FSM_QPLL_PD:01000000,FSM_QPLL_PDRESET:00100000,FSM_QPLLLOCK2:1010,FSM_IDLE:10000000,FSM_DRP_START_OPT:0111,FSM_QPLL_RESET:1001,FSM_QPLLLOCK:00010000,FSM_DRP_DONE_OPT:1000,FSM_DRP_DONE_NOM:00001000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[1]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[1] ),
        .R(mmcm_lock_reg1_reg_0));
  (* FSM_ENCODED_STATES = "FSM_MMCM_LOCK:00000010,FSM_DRP_START_NOM:00000100,FSM_WAIT_LOCK:00000001,FSM_QPLL_PD:01000000,FSM_QPLL_PDRESET:00100000,FSM_QPLLLOCK2:1010,FSM_IDLE:10000000,FSM_DRP_START_OPT:0111,FSM_QPLL_RESET:1001,FSM_QPLLLOCK:00010000,FSM_DRP_DONE_OPT:1000,FSM_DRP_DONE_NOM:00001000" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[2]_i_1_n_0 ),
        .Q(Q),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \cplllock_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(cplllock_reg1),
        .S(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \cplllock_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(cplllock_reg1),
        .Q(cplllock_reg2),
        .S(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \drp_done_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\drp_done_reg1_reg[0]_0 ),
        .Q(drp_done_reg1),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \drp_done_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(drp_done_reg1),
        .Q(drp_done_reg2),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(pipe_mmcm_lock_in),
        .Q(mmcm_lock_reg1),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE mmcm_lock_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(mmcm_lock_reg1),
        .Q(mmcm_lock_reg2),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \qplllock_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\qplllock_reg1_reg[0]_0 ),
        .Q(qplllock_reg1),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \qplllock_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(qplllock_reg1),
        .Q(qplllock_reg2),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \qpllpd_in_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(qpllpd_in_reg1),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \qpllpd_in_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(qpllpd_in_reg1),
        .Q(qpllpd_in_reg2),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \qpllreset_in_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(1'b0),
        .Q(qpllreset_in_reg1),
        .S(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDSE \qpllreset_in_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(qpllreset_in_reg1),
        .Q(qpllreset_in_reg2),
        .S(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rate_reg1_reg[1]_0 [0]),
        .Q(rate_reg1[0]),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\rate_reg1_reg[1]_0 [1]),
        .Q(rate_reg1[1]),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_reg1[0]),
        .Q(rate_reg2[0]),
        .R(mmcm_lock_reg1_reg_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \rate_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rate_reg1[1]),
        .Q(rate_reg2[1]),
        .R(mmcm_lock_reg1_reg_0));
endmodule

module pcie_7x_bridge_qpll_wrapper
   (cpllrst,
    qpll_drp_rdy,
    \gtp_common.gtpe2_common_i_0 ,
    \gtp_common.gtpe2_common_i_1 ,
    \gtp_common.gtpe2_common_i_2 ,
    D,
    gt_cpllpdrefclk,
    pipe_dclk_in,
    qpll_drp_en,
    qpll_drp_we,
    sys_clk,
    PLL0RESET0,
    \gtp_common.gtpe2_common_i_3 ,
    \gtp_common.gtpe2_common_i_4 );
  output cpllrst;
  output qpll_drp_rdy;
  output \gtp_common.gtpe2_common_i_0 ;
  output \gtp_common.gtpe2_common_i_1 ;
  output \gtp_common.gtpe2_common_i_2 ;
  output [15:0]D;
  input gt_cpllpdrefclk;
  input pipe_dclk_in;
  input qpll_drp_en;
  input qpll_drp_we;
  input sys_clk;
  input PLL0RESET0;
  input [15:0]\gtp_common.gtpe2_common_i_3 ;
  input [4:0]\gtp_common.gtpe2_common_i_4 ;

  wire [15:0]D;
  wire PLL0RESET0;
  wire cpllpd;
  wire cpllrst;
  wire gt_cpllpdrefclk;
  wire \gtp_common.gtpe2_common_i_0 ;
  wire \gtp_common.gtpe2_common_i_1 ;
  wire \gtp_common.gtpe2_common_i_2 ;
  wire [15:0]\gtp_common.gtpe2_common_i_3 ;
  wire [4:0]\gtp_common.gtpe2_common_i_4 ;
  wire pipe_dclk_in;
  wire qpll_drp_en;
  wire qpll_drp_rdy;
  wire qpll_drp_we;
  wire sys_clk;
  wire \NLW_gtp_common.gtpe2_common_i_PLL0FBCLKLOST_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL0REFCLKLOST_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL1FBCLKLOST_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL1LOCK_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL1OUTCLK_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL1OUTREFCLK_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_PLL1REFCLKLOST_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_REFCLKOUTMONITOR0_UNCONNECTED ;
  wire \NLW_gtp_common.gtpe2_common_i_REFCLKOUTMONITOR1_UNCONNECTED ;
  wire [7:0]\NLW_gtp_common.gtpe2_common_i_DMONITOROUT_UNCONNECTED ;
  wire [15:0]\NLW_gtp_common.gtpe2_common_i_PMARSVDOUT_UNCONNECTED ;

  pcie_7x_bridge_gtp_cpllpd_ovrd cpllPDInst
       (.cpllpd(cpllpd),
        .cpllrst(cpllrst),
        .gt_cpllpdrefclk(gt_cpllpdrefclk));
  (* BOX_TYPE = "PRIMITIVE" *) 
  GTPE2_COMMON #(
    .BIAS_CFG(64'h0000000000050001),
    .COMMON_CFG(32'h00000000),
    .IS_DRPCLK_INVERTED(1'b0),
    .IS_GTGREFCLK0_INVERTED(1'b0),
    .IS_GTGREFCLK1_INVERTED(1'b0),
    .IS_PLL0LOCKDETCLK_INVERTED(1'b0),
    .IS_PLL1LOCKDETCLK_INVERTED(1'b0),
    .PLL0_CFG(27'h01F024C),
    .PLL0_DMON_CFG(1'b0),
    .PLL0_FBDIV(5),
    .PLL0_FBDIV_45(5),
    .PLL0_INIT_CFG(24'h00001E),
    .PLL0_LOCK_CFG(9'h1E8),
    .PLL0_REFCLK_DIV(1),
    .PLL1_CFG(27'h01F024C),
    .PLL1_DMON_CFG(1'b0),
    .PLL1_FBDIV(5),
    .PLL1_FBDIV_45(5),
    .PLL1_INIT_CFG(24'h00001E),
    .PLL1_LOCK_CFG(9'h1E8),
    .PLL1_REFCLK_DIV(1),
    .PLL_CLKOUT_CFG(8'b00000000),
    .RSVD_ATTR0(16'h0000),
    .RSVD_ATTR1(16'h0000),
    .SIM_PLL0REFCLK_SEL(3'b001),
    .SIM_PLL1REFCLK_SEL(3'b001),
    .SIM_RESET_SPEEDUP("FALSE"),
    .SIM_VERSION("1.0")) 
    \gtp_common.gtpe2_common_i 
       (.BGBYPASSB(1'b1),
        .BGMONITORENB(1'b1),
        .BGPDB(1'b1),
        .BGRCALOVRD({1'b1,1'b1,1'b1,1'b1,1'b1}),
        .BGRCALOVRDENB(1'b1),
        .DMONITOROUT(\NLW_gtp_common.gtpe2_common_i_DMONITOROUT_UNCONNECTED [7:0]),
        .DRPADDR({\gtp_common.gtpe2_common_i_4 [4],1'b0,\gtp_common.gtpe2_common_i_4 [3],\gtp_common.gtpe2_common_i_4 [3],\gtp_common.gtpe2_common_i_4 [4],\gtp_common.gtpe2_common_i_4 [2:0]}),
        .DRPCLK(pipe_dclk_in),
        .DRPDI(\gtp_common.gtpe2_common_i_3 ),
        .DRPDO(D),
        .DRPEN(qpll_drp_en),
        .DRPRDY(qpll_drp_rdy),
        .DRPWE(qpll_drp_we),
        .GTEASTREFCLK0(1'b0),
        .GTEASTREFCLK1(1'b0),
        .GTGREFCLK0(1'b0),
        .GTGREFCLK1(1'b0),
        .GTREFCLK0(sys_clk),
        .GTREFCLK1(1'b0),
        .GTWESTREFCLK0(1'b0),
        .GTWESTREFCLK1(1'b0),
        .PLL0FBCLKLOST(\NLW_gtp_common.gtpe2_common_i_PLL0FBCLKLOST_UNCONNECTED ),
        .PLL0LOCK(\gtp_common.gtpe2_common_i_0 ),
        .PLL0LOCKDETCLK(1'b0),
        .PLL0LOCKEN(1'b1),
        .PLL0OUTCLK(\gtp_common.gtpe2_common_i_1 ),
        .PLL0OUTREFCLK(\gtp_common.gtpe2_common_i_2 ),
        .PLL0PD(cpllpd),
        .PLL0REFCLKLOST(\NLW_gtp_common.gtpe2_common_i_PLL0REFCLKLOST_UNCONNECTED ),
        .PLL0REFCLKSEL({1'b0,1'b0,1'b1}),
        .PLL0RESET(PLL0RESET0),
        .PLL1FBCLKLOST(\NLW_gtp_common.gtpe2_common_i_PLL1FBCLKLOST_UNCONNECTED ),
        .PLL1LOCK(\NLW_gtp_common.gtpe2_common_i_PLL1LOCK_UNCONNECTED ),
        .PLL1LOCKDETCLK(1'b0),
        .PLL1LOCKEN(1'b1),
        .PLL1OUTCLK(\NLW_gtp_common.gtpe2_common_i_PLL1OUTCLK_UNCONNECTED ),
        .PLL1OUTREFCLK(\NLW_gtp_common.gtpe2_common_i_PLL1OUTREFCLK_UNCONNECTED ),
        .PLL1PD(1'b1),
        .PLL1REFCLKLOST(\NLW_gtp_common.gtpe2_common_i_PLL1REFCLKLOST_UNCONNECTED ),
        .PLL1REFCLKSEL({1'b0,1'b0,1'b1}),
        .PLL1RESET(1'b1),
        .PLLRSVD1({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PLLRSVD2({1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PMARSVD({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .PMARSVDOUT(\NLW_gtp_common.gtpe2_common_i_PMARSVDOUT_UNCONNECTED [15:0]),
        .RCALENB(1'b1),
        .REFCLKOUTMONITOR0(\NLW_gtp_common.gtpe2_common_i_REFCLKOUTMONITOR0_UNCONNECTED ),
        .REFCLKOUTMONITOR1(\NLW_gtp_common.gtpe2_common_i_REFCLKOUTMONITOR1_UNCONNECTED ));
endmodule

module pcie_7x_bridge_rxeq_scan
   (adapt_done_reg_0,
    new_txcoeff_done_reg_0,
    D,
    rxeq_new_txcoeff_req_0,
    rst_cpllreset,
    rxeq_new_txcoeff_req,
    pipe_pclk_in,
    rxeq_preset_valid,
    out,
    rxeq_adapt_done_reg_reg,
    Q,
    rxeq_adapt_done_reg_reg_0,
    rxeq_adapt_done_reg_reg_1,
    rxeq_adapt_done_reg,
    rxeq_adapt_done,
    \FSM_onehot_fsm_rx_reg[5] ,
    \preset_reg1_reg[2]_0 ,
    \txpreset_reg1_reg[3]_0 ,
    \txcoeff_reg1_reg[17]_0 ,
    \fs_reg1_reg[5]_0 ,
    \lf_reg1_reg[5]_0 );
  output adapt_done_reg_0;
  output new_txcoeff_done_reg_0;
  output [2:0]D;
  output rxeq_new_txcoeff_req_0;
  input rst_cpllreset;
  input rxeq_new_txcoeff_req;
  input pipe_pclk_in;
  input rxeq_preset_valid;
  input [1:0]out;
  input rxeq_adapt_done_reg_reg;
  input [4:0]Q;
  input rxeq_adapt_done_reg_reg_0;
  input rxeq_adapt_done_reg_reg_1;
  input rxeq_adapt_done_reg;
  input rxeq_adapt_done;
  input [2:0]\FSM_onehot_fsm_rx_reg[5] ;
  input [2:0]\preset_reg1_reg[2]_0 ;
  input [3:0]\txpreset_reg1_reg[3]_0 ;
  input [17:0]\txcoeff_reg1_reg[17]_0 ;
  input [5:0]\fs_reg1_reg[5]_0 ;
  input [5:0]\lf_reg1_reg[5]_0 ;

  wire [2:0]D;
  wire \FSM_onehot_fsm[1]_i_1_n_0 ;
  wire \FSM_onehot_fsm[2]_i_1_n_0 ;
  wire \FSM_onehot_fsm[3]_i_1__0_n_0 ;
  wire \FSM_onehot_fsm[3]_i_2_n_0 ;
  wire \FSM_onehot_fsm[4]_i_10_n_0 ;
  wire \FSM_onehot_fsm[4]_i_11_n_0 ;
  wire \FSM_onehot_fsm[4]_i_12_n_0 ;
  wire \FSM_onehot_fsm[4]_i_13_n_0 ;
  wire \FSM_onehot_fsm[4]_i_1_n_0 ;
  wire \FSM_onehot_fsm[4]_i_2_n_0 ;
  wire \FSM_onehot_fsm[4]_i_3_n_0 ;
  wire \FSM_onehot_fsm[4]_i_4_n_0 ;
  wire \FSM_onehot_fsm[4]_i_5_n_0 ;
  wire \FSM_onehot_fsm[4]_i_6_n_0 ;
  wire \FSM_onehot_fsm[4]_i_7_n_0 ;
  wire \FSM_onehot_fsm[4]_i_8_n_0 ;
  wire \FSM_onehot_fsm[4]_i_9_n_0 ;
  wire \FSM_onehot_fsm_reg_n_0_[1] ;
  wire \FSM_onehot_fsm_reg_n_0_[2] ;
  wire \FSM_onehot_fsm_reg_n_0_[3] ;
  wire \FSM_onehot_fsm_reg_n_0_[4] ;
  wire \FSM_onehot_fsm_rx[6]_i_2_n_0 ;
  wire [2:0]\FSM_onehot_fsm_rx_reg[5] ;
  wire [4:0]Q;
  wire adapt_done;
  wire adapt_done_cnt_i_1_n_0;
  wire adapt_done_cnt_i_2_n_0;
  wire adapt_done_cnt_reg_n_0;
  wire adapt_done_reg_0;
  wire [21:0]converge_cnt;
  wire [21:0]converge_cnt0;
  wire \converge_cnt[3]_i_3_n_0 ;
  wire \converge_cnt_reg[11]_i_2_n_0 ;
  wire \converge_cnt_reg[11]_i_2_n_1 ;
  wire \converge_cnt_reg[11]_i_2_n_2 ;
  wire \converge_cnt_reg[11]_i_2_n_3 ;
  wire \converge_cnt_reg[15]_i_2_n_0 ;
  wire \converge_cnt_reg[15]_i_2_n_1 ;
  wire \converge_cnt_reg[15]_i_2_n_2 ;
  wire \converge_cnt_reg[15]_i_2_n_3 ;
  wire \converge_cnt_reg[19]_i_2_n_0 ;
  wire \converge_cnt_reg[19]_i_2_n_1 ;
  wire \converge_cnt_reg[19]_i_2_n_2 ;
  wire \converge_cnt_reg[19]_i_2_n_3 ;
  wire \converge_cnt_reg[21]_i_2_n_3 ;
  wire \converge_cnt_reg[3]_i_2_n_0 ;
  wire \converge_cnt_reg[3]_i_2_n_1 ;
  wire \converge_cnt_reg[3]_i_2_n_2 ;
  wire \converge_cnt_reg[3]_i_2_n_3 ;
  wire \converge_cnt_reg[7]_i_2_n_0 ;
  wire \converge_cnt_reg[7]_i_2_n_1 ;
  wire \converge_cnt_reg[7]_i_2_n_2 ;
  wire \converge_cnt_reg[7]_i_2_n_3 ;
  wire \converge_cnt_reg_n_0_[0] ;
  wire \converge_cnt_reg_n_0_[10] ;
  wire \converge_cnt_reg_n_0_[11] ;
  wire \converge_cnt_reg_n_0_[12] ;
  wire \converge_cnt_reg_n_0_[13] ;
  wire \converge_cnt_reg_n_0_[14] ;
  wire \converge_cnt_reg_n_0_[15] ;
  wire \converge_cnt_reg_n_0_[16] ;
  wire \converge_cnt_reg_n_0_[17] ;
  wire \converge_cnt_reg_n_0_[18] ;
  wire \converge_cnt_reg_n_0_[19] ;
  wire \converge_cnt_reg_n_0_[1] ;
  wire \converge_cnt_reg_n_0_[20] ;
  wire \converge_cnt_reg_n_0_[21] ;
  wire \converge_cnt_reg_n_0_[2] ;
  wire \converge_cnt_reg_n_0_[3] ;
  wire \converge_cnt_reg_n_0_[4] ;
  wire \converge_cnt_reg_n_0_[5] ;
  wire \converge_cnt_reg_n_0_[6] ;
  wire \converge_cnt_reg_n_0_[7] ;
  wire \converge_cnt_reg_n_0_[8] ;
  wire \converge_cnt_reg_n_0_[9] ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]fs_reg1;
  wire [5:0]\fs_reg1_reg[5]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]fs_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]lf_reg1;
  wire [5:0]\lf_reg1_reg[5]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [5:0]lf_reg2;
  wire new_txcoeff_done;
  wire new_txcoeff_done_reg_0;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire new_txcoeff_req_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire new_txcoeff_req_reg2;
  wire [1:0]out;
  wire pipe_pclk_in;
  wire preset_done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [2:0]preset_reg1;
  wire [2:0]\preset_reg1_reg[2]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [2:0]preset_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire preset_valid_reg1;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire preset_valid_reg2;
  wire rst_cpllreset;
  wire rxeq_adapt_done;
  wire rxeq_adapt_done_reg;
  wire rxeq_adapt_done_reg_reg;
  wire rxeq_adapt_done_reg_reg_0;
  wire rxeq_adapt_done_reg_reg_1;
  wire rxeq_new_txcoeff_req;
  wire rxeq_new_txcoeff_req_0;
  wire rxeq_preset_valid;
  wire rxeqscan_adapt_done;
  wire rxeqscan_new_txcoeff_done;
  wire rxeqscan_preset_done;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [17:0]txcoeff_reg1;
  wire [17:0]\txcoeff_reg1_reg[17]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [17:0]txcoeff_reg2;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]txpreset_reg1;
  wire [3:0]\txpreset_reg1_reg[3]_0 ;
  (* SHIFT_EXTRACT = "NO" *) (* async_reg = "true" *) wire [3:0]txpreset_reg2;
  wire [3:1]\NLW_converge_cnt_reg[21]_i_2_CO_UNCONNECTED ;
  wire [3:2]\NLW_converge_cnt_reg[21]_i_2_O_UNCONNECTED ;

  LUT6 #(
    .INIT(64'h0F00AFAF0F11AFBB)) 
    \FSM_onehot_fsm[1]_i_1 
       (.I0(\FSM_onehot_fsm_reg_n_0_[4] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(preset_valid_reg2),
        .I3(\FSM_onehot_fsm_reg_n_0_[2] ),
        .I4(new_txcoeff_req_reg2),
        .I5(\FSM_onehot_fsm_reg_n_0_[1] ),
        .O(\FSM_onehot_fsm[1]_i_1_n_0 ));
  LUT3 #(
    .INIT(8'hA8)) 
    \FSM_onehot_fsm[2]_i_1 
       (.I0(preset_valid_reg2),
        .I1(\FSM_onehot_fsm_reg_n_0_[2] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[1] ),
        .O(\FSM_onehot_fsm[2]_i_1_n_0 ));
  LUT6 #(
    .INIT(64'h10FF101010101010)) 
    \FSM_onehot_fsm[3]_i_1__0 
       (.I0(\FSM_onehot_fsm[4]_i_3_n_0 ),
        .I1(\FSM_onehot_fsm[3]_i_2_n_0 ),
        .I2(\FSM_onehot_fsm[4]_i_2_n_0 ),
        .I3(preset_valid_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[1] ),
        .I5(new_txcoeff_req_reg2),
        .O(\FSM_onehot_fsm[3]_i_1__0_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair27" *) 
  LUT4 #(
    .INIT(16'h04FF)) 
    \FSM_onehot_fsm[3]_i_2 
       (.I0(adapt_done_cnt_reg_n_0),
        .I1(out[1]),
        .I2(out[0]),
        .I3(\FSM_onehot_fsm_reg_n_0_[3] ),
        .O(\FSM_onehot_fsm[3]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFD0FFD0FFD0)) 
    \FSM_onehot_fsm[4]_i_1 
       (.I0(\FSM_onehot_fsm[4]_i_2_n_0 ),
        .I1(\FSM_onehot_fsm[4]_i_3_n_0 ),
        .I2(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I3(\FSM_onehot_fsm[4]_i_4_n_0 ),
        .I4(\FSM_onehot_fsm_reg_n_0_[4] ),
        .I5(new_txcoeff_req_reg2),
        .O(\FSM_onehot_fsm[4]_i_1_n_0 ));
  LUT5 #(
    .INIT(32'hFFFFFFEF)) 
    \FSM_onehot_fsm[4]_i_10 
       (.I0(\converge_cnt_reg_n_0_[2] ),
        .I1(\converge_cnt_reg_n_0_[14] ),
        .I2(out[1]),
        .I3(out[0]),
        .I4(\FSM_onehot_fsm[4]_i_13_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_10_n_0 ));
  LUT4 #(
    .INIT(16'hFF7F)) 
    \FSM_onehot_fsm[4]_i_11 
       (.I0(\converge_cnt_reg_n_0_[20] ),
        .I1(\converge_cnt_reg_n_0_[0] ),
        .I2(\converge_cnt_reg_n_0_[14] ),
        .I3(\converge_cnt_reg_n_0_[1] ),
        .O(\FSM_onehot_fsm[4]_i_11_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair28" *) 
  LUT5 #(
    .INIT(32'hFFFFFFFE)) 
    \FSM_onehot_fsm[4]_i_12 
       (.I0(\converge_cnt_reg_n_0_[4] ),
        .I1(\converge_cnt_reg_n_0_[5] ),
        .I2(\converge_cnt_reg_n_0_[7] ),
        .I3(\converge_cnt_reg_n_0_[6] ),
        .I4(\FSM_onehot_fsm[4]_i_9_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_12_n_0 ));
  LUT4 #(
    .INIT(16'hFFDF)) 
    \FSM_onehot_fsm[4]_i_13 
       (.I0(\converge_cnt_reg_n_0_[15] ),
        .I1(\converge_cnt_reg_n_0_[0] ),
        .I2(\converge_cnt_reg_n_0_[11] ),
        .I3(\converge_cnt_reg_n_0_[1] ),
        .O(\FSM_onehot_fsm[4]_i_13_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFBFFFFFFF)) 
    \FSM_onehot_fsm[4]_i_2 
       (.I0(\FSM_onehot_fsm[4]_i_5_n_0 ),
        .I1(\converge_cnt_reg_n_0_[3] ),
        .I2(\converge_cnt_reg_n_0_[13] ),
        .I3(\converge_cnt_reg_n_0_[10] ),
        .I4(\converge_cnt_reg_n_0_[8] ),
        .I5(\FSM_onehot_fsm[4]_i_6_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h0000000000001000)) 
    \FSM_onehot_fsm[4]_i_3 
       (.I0(\FSM_onehot_fsm[4]_i_7_n_0 ),
        .I1(\converge_cnt_reg_n_0_[3] ),
        .I2(\converge_cnt_reg_n_0_[15] ),
        .I3(\converge_cnt_reg_n_0_[2] ),
        .I4(\converge_cnt_reg_n_0_[8] ),
        .I5(\FSM_onehot_fsm[4]_i_8_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_3_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair26" *) 
  LUT4 #(
    .INIT(16'h0400)) 
    \FSM_onehot_fsm[4]_i_4 
       (.I0(adapt_done_cnt_reg_n_0),
        .I1(out[1]),
        .I2(out[0]),
        .I3(\FSM_onehot_fsm_reg_n_0_[3] ),
        .O(\FSM_onehot_fsm[4]_i_4_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFEFFF)) 
    \FSM_onehot_fsm[4]_i_5 
       (.I0(\converge_cnt_reg_n_0_[20] ),
        .I1(\converge_cnt_reg_n_0_[12] ),
        .I2(\converge_cnt_reg_n_0_[21] ),
        .I3(\converge_cnt_reg_n_0_[9] ),
        .I4(\FSM_onehot_fsm[4]_i_9_n_0 ),
        .I5(\FSM_onehot_fsm[4]_i_10_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_5_n_0 ));
  (* SOFT_HLUTNM = "soft_lutpair28" *) 
  LUT4 #(
    .INIT(16'hFFFE)) 
    \FSM_onehot_fsm[4]_i_6 
       (.I0(\converge_cnt_reg_n_0_[6] ),
        .I1(\converge_cnt_reg_n_0_[7] ),
        .I2(\converge_cnt_reg_n_0_[5] ),
        .I3(\converge_cnt_reg_n_0_[4] ),
        .O(\FSM_onehot_fsm[4]_i_6_n_0 ));
  LUT4 #(
    .INIT(16'hFF4F)) 
    \FSM_onehot_fsm[4]_i_7 
       (.I0(out[0]),
        .I1(out[1]),
        .I2(\converge_cnt_reg_n_0_[11] ),
        .I3(\converge_cnt_reg_n_0_[13] ),
        .O(\FSM_onehot_fsm[4]_i_7_n_0 ));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFFFFEFF)) 
    \FSM_onehot_fsm[4]_i_8 
       (.I0(\FSM_onehot_fsm[4]_i_11_n_0 ),
        .I1(\converge_cnt_reg_n_0_[21] ),
        .I2(\converge_cnt_reg_n_0_[12] ),
        .I3(\converge_cnt_reg_n_0_[9] ),
        .I4(\converge_cnt_reg_n_0_[10] ),
        .I5(\FSM_onehot_fsm[4]_i_12_n_0 ),
        .O(\FSM_onehot_fsm[4]_i_8_n_0 ));
  LUT4 #(
    .INIT(16'h7FFF)) 
    \FSM_onehot_fsm[4]_i_9 
       (.I0(\converge_cnt_reg_n_0_[18] ),
        .I1(\converge_cnt_reg_n_0_[19] ),
        .I2(\converge_cnt_reg_n_0_[16] ),
        .I3(\converge_cnt_reg_n_0_[17] ),
        .O(\FSM_onehot_fsm[4]_i_9_n_0 ));
  (* FSM_ENCODED_STATES = "FSM_PRESET:00100,FSM_CONVERGE:01000,FSM_NEW_TXCOEFF_REQ:10000,FSM_IDLE:00010,iSTATE:00001" *) 
  FDSE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[1]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[1] ),
        .S(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_PRESET:00100,FSM_CONVERGE:01000,FSM_NEW_TXCOEFF_REQ:10000,FSM_IDLE:00010,iSTATE:00001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[2]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[2] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_PRESET:00100,FSM_CONVERGE:01000,FSM_NEW_TXCOEFF_REQ:10000,FSM_IDLE:00010,iSTATE:00001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[3]_i_1__0_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[3] ),
        .R(rst_cpllreset));
  (* FSM_ENCODED_STATES = "FSM_PRESET:00100,FSM_CONVERGE:01000,FSM_NEW_TXCOEFF_REQ:10000,FSM_IDLE:00010,iSTATE:00001" *) 
  FDRE #(
    .INIT(1'b0)) 
    \FSM_onehot_fsm_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\FSM_onehot_fsm[4]_i_1_n_0 ),
        .Q(\FSM_onehot_fsm_reg_n_0_[4] ),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'h40FF4040)) 
    \FSM_onehot_fsm_rx[2]_i_1 
       (.I0(out[1]),
        .I1(out[0]),
        .I2(Q[0]),
        .I3(rxeqscan_preset_done),
        .I4(Q[1]),
        .O(D[0]));
  LUT6 #(
    .INIT(64'hF444444444444444)) 
    \FSM_onehot_fsm_rx[5]_i_1 
       (.I0(rxeqscan_new_txcoeff_done),
        .I1(Q[3]),
        .I2(\FSM_onehot_fsm_rx_reg[5] [2]),
        .I3(\FSM_onehot_fsm_rx_reg[5] [1]),
        .I4(\FSM_onehot_fsm_rx_reg[5] [0]),
        .I5(Q[2]),
        .O(D[1]));
  LUT6 #(
    .INIT(64'hFFFFFFFFFFE0E0E0)) 
    \FSM_onehot_fsm_rx[6]_i_1 
       (.I0(out[0]),
        .I1(out[1]),
        .I2(Q[4]),
        .I3(Q[1]),
        .I4(rxeqscan_preset_done),
        .I5(\FSM_onehot_fsm_rx[6]_i_2_n_0 ),
        .O(D[2]));
  (* SOFT_HLUTNM = "soft_lutpair29" *) 
  LUT2 #(
    .INIT(4'h8)) 
    \FSM_onehot_fsm_rx[6]_i_2 
       (.I0(rxeqscan_new_txcoeff_done),
        .I1(Q[3]),
        .O(\FSM_onehot_fsm_rx[6]_i_2_n_0 ));
  LUT6 #(
    .INIT(64'h00000AAAFFFF0800)) 
    adapt_done_cnt_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[4] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .I5(adapt_done_cnt_i_2_n_0),
        .O(adapt_done_cnt_i_1_n_0));
  LUT5 #(
    .INIT(32'h00FF0101)) 
    adapt_done_cnt_i_2
       (.I0(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I1(\FSM_onehot_fsm_reg_n_0_[2] ),
        .I2(\FSM_onehot_fsm_reg_n_0_[1] ),
        .I3(new_txcoeff_req_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[4] ),
        .O(adapt_done_cnt_i_2_n_0));
  FDRE #(
    .INIT(1'b0)) 
    adapt_done_cnt_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(adapt_done_cnt_i_1_n_0),
        .Q(adapt_done_cnt_reg_n_0),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'hF8000000)) 
    adapt_done_i_1
       (.I0(out[0]),
        .I1(out[1]),
        .I2(adapt_done_cnt_reg_n_0),
        .I3(new_txcoeff_req_reg2),
        .I4(\FSM_onehot_fsm_reg_n_0_[4] ),
        .O(adapt_done));
  FDRE #(
    .INIT(1'b0)) 
    adapt_done_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(adapt_done),
        .Q(rxeqscan_adapt_done),
        .R(rst_cpllreset));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[0]_i_1 
       (.I0(converge_cnt0[0]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[0]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[10]_i_1 
       (.I0(converge_cnt0[10]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[10]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[11]_i_1 
       (.I0(converge_cnt0[11]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[11]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[12]_i_1 
       (.I0(converge_cnt0[12]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[12]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[13]_i_1 
       (.I0(converge_cnt0[13]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[13]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[14]_i_1 
       (.I0(converge_cnt0[14]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[14]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[15]_i_1 
       (.I0(converge_cnt0[15]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[15]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[16]_i_1 
       (.I0(converge_cnt0[16]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[16]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[17]_i_1 
       (.I0(converge_cnt0[17]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[17]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[18]_i_1 
       (.I0(converge_cnt0[18]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[18]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[19]_i_1 
       (.I0(converge_cnt0[19]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[19]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[1]_i_1 
       (.I0(converge_cnt0[1]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[1]));
  (* SOFT_HLUTNM = "soft_lutpair27" *) 
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[20]_i_1 
       (.I0(converge_cnt0[20]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[20]));
  (* SOFT_HLUTNM = "soft_lutpair26" *) 
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[21]_i_1 
       (.I0(converge_cnt0[21]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[21]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[2]_i_1 
       (.I0(converge_cnt0[2]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[2]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[3]_i_1 
       (.I0(converge_cnt0[3]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[3]));
  LUT1 #(
    .INIT(2'h1)) 
    \converge_cnt[3]_i_3 
       (.I0(\converge_cnt_reg_n_0_[0] ),
        .O(\converge_cnt[3]_i_3_n_0 ));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[4]_i_1 
       (.I0(converge_cnt0[4]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[4]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[5]_i_1 
       (.I0(converge_cnt0[5]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[5]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[6]_i_1 
       (.I0(converge_cnt0[6]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[6]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[7]_i_1 
       (.I0(converge_cnt0[7]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[7]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[8]_i_1 
       (.I0(converge_cnt0[8]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[8]));
  LUT5 #(
    .INIT(32'h88888088)) 
    \converge_cnt[9]_i_1 
       (.I0(converge_cnt0[9]),
        .I1(\FSM_onehot_fsm_reg_n_0_[3] ),
        .I2(out[0]),
        .I3(out[1]),
        .I4(adapt_done_cnt_reg_n_0),
        .O(converge_cnt[9]));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[0]),
        .Q(\converge_cnt_reg_n_0_[0] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[10]),
        .Q(\converge_cnt_reg_n_0_[10] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[11]),
        .Q(\converge_cnt_reg_n_0_[11] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[11]_i_2 
       (.CI(\converge_cnt_reg[7]_i_2_n_0 ),
        .CO({\converge_cnt_reg[11]_i_2_n_0 ,\converge_cnt_reg[11]_i_2_n_1 ,\converge_cnt_reg[11]_i_2_n_2 ,\converge_cnt_reg[11]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(converge_cnt0[11:8]),
        .S({\converge_cnt_reg_n_0_[11] ,\converge_cnt_reg_n_0_[10] ,\converge_cnt_reg_n_0_[9] ,\converge_cnt_reg_n_0_[8] }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[12]),
        .Q(\converge_cnt_reg_n_0_[12] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[13]),
        .Q(\converge_cnt_reg_n_0_[13] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[14]),
        .Q(\converge_cnt_reg_n_0_[14] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[15]),
        .Q(\converge_cnt_reg_n_0_[15] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[15]_i_2 
       (.CI(\converge_cnt_reg[11]_i_2_n_0 ),
        .CO({\converge_cnt_reg[15]_i_2_n_0 ,\converge_cnt_reg[15]_i_2_n_1 ,\converge_cnt_reg[15]_i_2_n_2 ,\converge_cnt_reg[15]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(converge_cnt0[15:12]),
        .S({\converge_cnt_reg_n_0_[15] ,\converge_cnt_reg_n_0_[14] ,\converge_cnt_reg_n_0_[13] ,\converge_cnt_reg_n_0_[12] }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[16] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[16]),
        .Q(\converge_cnt_reg_n_0_[16] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[17]),
        .Q(\converge_cnt_reg_n_0_[17] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[18] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[18]),
        .Q(\converge_cnt_reg_n_0_[18] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[19] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[19]),
        .Q(\converge_cnt_reg_n_0_[19] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[19]_i_2 
       (.CI(\converge_cnt_reg[15]_i_2_n_0 ),
        .CO({\converge_cnt_reg[19]_i_2_n_0 ,\converge_cnt_reg[19]_i_2_n_1 ,\converge_cnt_reg[19]_i_2_n_2 ,\converge_cnt_reg[19]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(converge_cnt0[19:16]),
        .S({\converge_cnt_reg_n_0_[19] ,\converge_cnt_reg_n_0_[18] ,\converge_cnt_reg_n_0_[17] ,\converge_cnt_reg_n_0_[16] }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[1]),
        .Q(\converge_cnt_reg_n_0_[1] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[20] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[20]),
        .Q(\converge_cnt_reg_n_0_[20] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[21] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[21]),
        .Q(\converge_cnt_reg_n_0_[21] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[21]_i_2 
       (.CI(\converge_cnt_reg[19]_i_2_n_0 ),
        .CO({\NLW_converge_cnt_reg[21]_i_2_CO_UNCONNECTED [3:1],\converge_cnt_reg[21]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O({\NLW_converge_cnt_reg[21]_i_2_O_UNCONNECTED [3:2],converge_cnt0[21:20]}),
        .S({1'b0,1'b0,\converge_cnt_reg_n_0_[21] ,\converge_cnt_reg_n_0_[20] }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[2]),
        .Q(\converge_cnt_reg_n_0_[2] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[3]),
        .Q(\converge_cnt_reg_n_0_[3] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[3]_i_2 
       (.CI(1'b0),
        .CO({\converge_cnt_reg[3]_i_2_n_0 ,\converge_cnt_reg[3]_i_2_n_1 ,\converge_cnt_reg[3]_i_2_n_2 ,\converge_cnt_reg[3]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,\converge_cnt_reg_n_0_[0] }),
        .O(converge_cnt0[3:0]),
        .S({\converge_cnt_reg_n_0_[3] ,\converge_cnt_reg_n_0_[2] ,\converge_cnt_reg_n_0_[1] ,\converge_cnt[3]_i_3_n_0 }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[4]),
        .Q(\converge_cnt_reg_n_0_[4] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[5]),
        .Q(\converge_cnt_reg_n_0_[5] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[6]),
        .Q(\converge_cnt_reg_n_0_[6] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[7]),
        .Q(\converge_cnt_reg_n_0_[7] ),
        .R(rst_cpllreset));
  (* ADDER_THRESHOLD = "35" *) 
  CARRY4 \converge_cnt_reg[7]_i_2 
       (.CI(\converge_cnt_reg[3]_i_2_n_0 ),
        .CO({\converge_cnt_reg[7]_i_2_n_0 ,\converge_cnt_reg[7]_i_2_n_1 ,\converge_cnt_reg[7]_i_2_n_2 ,\converge_cnt_reg[7]_i_2_n_3 }),
        .CYINIT(1'b0),
        .DI({1'b0,1'b0,1'b0,1'b0}),
        .O(converge_cnt0[7:4]),
        .S({\converge_cnt_reg_n_0_[7] ,\converge_cnt_reg_n_0_[6] ,\converge_cnt_reg_n_0_[5] ,\converge_cnt_reg_n_0_[4] }));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[8]),
        .Q(\converge_cnt_reg_n_0_[8] ),
        .R(rst_cpllreset));
  FDRE #(
    .INIT(1'b0)) 
    \converge_cnt_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(converge_cnt[9]),
        .Q(\converge_cnt_reg_n_0_[9] ),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [0]),
        .Q(fs_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [1]),
        .Q(fs_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [2]),
        .Q(fs_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [3]),
        .Q(fs_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [4]),
        .Q(fs_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\fs_reg1_reg[5]_0 [5]),
        .Q(fs_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[0]),
        .Q(fs_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[1]),
        .Q(fs_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[2]),
        .Q(fs_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[3]),
        .Q(fs_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[4]),
        .Q(fs_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \fs_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(fs_reg1[5]),
        .Q(fs_reg2[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [0]),
        .Q(lf_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [1]),
        .Q(lf_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [2]),
        .Q(lf_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [3]),
        .Q(lf_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [4]),
        .Q(lf_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\lf_reg1_reg[5]_0 [5]),
        .Q(lf_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[0]),
        .Q(lf_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[1]),
        .Q(lf_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[2]),
        .Q(lf_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[3]),
        .Q(lf_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[4]),
        .Q(lf_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \lf_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(lf_reg1[5]),
        .Q(lf_reg2[5]),
        .R(rst_cpllreset));
  LUT2 #(
    .INIT(4'h8)) 
    new_txcoeff_done_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[4] ),
        .I1(new_txcoeff_req_reg2),
        .O(new_txcoeff_done));
  FDRE #(
    .INIT(1'b0)) 
    new_txcoeff_done_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(new_txcoeff_done),
        .Q(rxeqscan_new_txcoeff_done),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE new_txcoeff_req_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_new_txcoeff_req),
        .Q(new_txcoeff_req_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE new_txcoeff_req_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(new_txcoeff_req_reg1),
        .Q(new_txcoeff_req_reg2),
        .R(rst_cpllreset));
  LUT3 #(
    .INIT(8'hEA)) 
    preset_done_i_1
       (.I0(\FSM_onehot_fsm_reg_n_0_[2] ),
        .I1(preset_valid_reg2),
        .I2(\FSM_onehot_fsm_reg_n_0_[1] ),
        .O(preset_done));
  FDRE #(
    .INIT(1'b0)) 
    preset_done_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(preset_done),
        .Q(rxeqscan_preset_done),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\preset_reg1_reg[2]_0 [0]),
        .Q(preset_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\preset_reg1_reg[2]_0 [1]),
        .Q(preset_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\preset_reg1_reg[2]_0 [2]),
        .Q(preset_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(preset_reg1[0]),
        .Q(preset_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(preset_reg1[1]),
        .Q(preset_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \preset_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(preset_reg1[2]),
        .Q(preset_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE preset_valid_reg1_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(rxeq_preset_valid),
        .Q(preset_valid_reg1),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE preset_valid_reg2_reg
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(preset_valid_reg1),
        .Q(preset_valid_reg2),
        .R(rst_cpllreset));
  LUT6 #(
    .INIT(64'hA800FFFFA8000000)) 
    rxeq_adapt_done_i_1
       (.I0(rxeqscan_new_txcoeff_done),
        .I1(rxeq_adapt_done_reg_reg_1),
        .I2(rxeqscan_adapt_done),
        .I3(Q[3]),
        .I4(rxeq_adapt_done_reg),
        .I5(rxeq_adapt_done),
        .O(new_txcoeff_done_reg_0));
  LUT6 #(
    .INIT(64'hFF00FF33AA00A800)) 
    rxeq_adapt_done_reg_i_1
       (.I0(rxeqscan_adapt_done),
        .I1(rxeq_adapt_done_reg_reg),
        .I2(rxeqscan_new_txcoeff_done),
        .I3(Q[3]),
        .I4(rxeq_adapt_done_reg_reg_0),
        .I5(rxeq_adapt_done_reg_reg_1),
        .O(adapt_done_reg_0));
  (* SOFT_HLUTNM = "soft_lutpair29" *) 
  LUT2 #(
    .INIT(4'h2)) 
    rxeq_new_txcoeff_req_i_1
       (.I0(Q[3]),
        .I1(rxeqscan_new_txcoeff_done),
        .O(rxeq_new_txcoeff_req_0));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [0]),
        .Q(txcoeff_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [10]),
        .Q(txcoeff_reg1[10]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [11]),
        .Q(txcoeff_reg1[11]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [12]),
        .Q(txcoeff_reg1[12]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [13]),
        .Q(txcoeff_reg1[13]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [14]),
        .Q(txcoeff_reg1[14]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [15]),
        .Q(txcoeff_reg1[15]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[16] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [16]),
        .Q(txcoeff_reg1[16]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [17]),
        .Q(txcoeff_reg1[17]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [1]),
        .Q(txcoeff_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [2]),
        .Q(txcoeff_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [3]),
        .Q(txcoeff_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [4]),
        .Q(txcoeff_reg1[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [5]),
        .Q(txcoeff_reg1[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [6]),
        .Q(txcoeff_reg1[6]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [7]),
        .Q(txcoeff_reg1[7]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [8]),
        .Q(txcoeff_reg1[8]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg1_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txcoeff_reg1_reg[17]_0 [9]),
        .Q(txcoeff_reg1[9]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[0]),
        .Q(txcoeff_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[10] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[10]),
        .Q(txcoeff_reg2[10]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[11] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[11]),
        .Q(txcoeff_reg2[11]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[12] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[12]),
        .Q(txcoeff_reg2[12]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[13] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[13]),
        .Q(txcoeff_reg2[13]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[14] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[14]),
        .Q(txcoeff_reg2[14]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[15] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[15]),
        .Q(txcoeff_reg2[15]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[16] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[16]),
        .Q(txcoeff_reg2[16]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[17] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[17]),
        .Q(txcoeff_reg2[17]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[1]),
        .Q(txcoeff_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[2]),
        .Q(txcoeff_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[3]),
        .Q(txcoeff_reg2[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[4] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[4]),
        .Q(txcoeff_reg2[4]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[5] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[5]),
        .Q(txcoeff_reg2[5]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[6] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[6]),
        .Q(txcoeff_reg2[6]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[7] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[7]),
        .Q(txcoeff_reg2[7]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[8] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[8]),
        .Q(txcoeff_reg2[8]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txcoeff_reg2_reg[9] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txcoeff_reg1[9]),
        .Q(txcoeff_reg2[9]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg1_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txpreset_reg1_reg[3]_0 [0]),
        .Q(txpreset_reg1[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg1_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txpreset_reg1_reg[3]_0 [1]),
        .Q(txpreset_reg1[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg1_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txpreset_reg1_reg[3]_0 [2]),
        .Q(txpreset_reg1[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg1_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(\txpreset_reg1_reg[3]_0 [3]),
        .Q(txpreset_reg1[3]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg2_reg[0] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txpreset_reg1[0]),
        .Q(txpreset_reg2[0]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg2_reg[1] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txpreset_reg1[1]),
        .Q(txpreset_reg2[1]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg2_reg[2] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txpreset_reg1[2]),
        .Q(txpreset_reg2[2]),
        .R(rst_cpllreset));
  (* ASYNC_REG *) 
  (* KEEP = "yes" *) 
  (* SHIFT_EXTRACT = "NO" *) 
  FDRE \txpreset_reg2_reg[3] 
       (.C(pipe_pclk_in),
        .CE(1'b1),
        .D(txpreset_reg1[3]),
        .Q(txpreset_reg2[3]),
        .R(rst_cpllreset));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [14:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [14:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_52 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_53 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_74 ;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [14:0]rdata;
  wire [14:0]wdata;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMTXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMTXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],1'b0,1'b0,wdata[14:9],wdata[7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,1'b0,wdata[8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_52 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_53 ,rdata[14:9],rdata[7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_74 ,rdata[8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_tx_wen),
        .ENBWREN(mim_tx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_11
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 );
  output [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire [13:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_52 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_53 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_54 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_74 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMRXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMRXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [13:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,1'b0,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_52 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_53 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_54 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [13:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_74 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_rx_wen),
        .ENBWREN(mim_rx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_12
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMRXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMRXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_rx_wen),
        .ENBWREN(mim_rx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_13
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMRXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMRXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_rx_wen),
        .ENBWREN(mim_rx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_14
   (\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ,
    pipe_userclk1_in,
    mim_rx_wen,
    mim_rx_ren,
    MIMRXWADDR,
    MIMRXRADDR,
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 );
  output [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  input pipe_userclk1_in;
  input mim_rx_wen;
  input mim_rx_ren;
  input [10:0]MIMRXWADDR;
  input [10:0]MIMRXRADDR;
  input [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;

  wire [10:0]MIMRXRADDR;
  wire [10:0]MIMRXWADDR;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 ;
  wire [17:0]\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_rx_ren;
  wire mim_rx_wen;
  wire pipe_userclk1_in;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMRXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMRXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_1 [8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [16:9],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [17],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_0 [8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_rx_wen),
        .ENBWREN(mim_rx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_4
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMTXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMTXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],wdata[16:9],wdata[7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,wdata[17],wdata[8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],rdata[16:9],rdata[7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],rdata[17],rdata[8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_tx_wen),
        .ENBWREN(mim_tx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_5
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMTXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMTXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],wdata[16:9],wdata[7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,wdata[17],wdata[8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],rdata[16:9],rdata[7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],rdata[17],rdata[8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_tx_wen),
        .ENBWREN(mim_tx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* ORIG_REF_NAME = "xil_internal_svlib_BRAM_TDP_MACRO" *) 
module pcie_7x_bridge_xil_internal_svlib_BRAM_TDP_MACRO_6
   (rdata,
    pipe_userclk1_in,
    mim_tx_wen,
    mim_tx_ren,
    MIMTXWADDR,
    MIMTXRADDR,
    wdata);
  output [17:0]rdata;
  input pipe_userclk1_in;
  input mim_tx_wen;
  input mim_tx_ren;
  input [10:0]MIMTXWADDR;
  input [10:0]MIMTXRADDR;
  input [17:0]wdata;

  wire [10:0]MIMTXRADDR;
  wire [10:0]MIMTXWADDR;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ;
  wire \genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 ;
  wire mim_tx_ren;
  wire mim_tx_wen;
  wire pipe_userclk1_in;
  wire [17:0]rdata;
  wire [17:0]wdata;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ;
  wire \NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED ;
  wire [31:16]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED ;
  wire [3:2]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED ;
  wire [7:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED ;
  wire [8:0]\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED ;

  (* BOX_TYPE = "PRIMITIVE" *) 
  RAMB36E1 #(
    .DOA_REG(0),
    .DOB_REG(1),
    .EN_ECC_READ("FALSE"),
    .EN_ECC_WRITE("FALSE"),
    .INITP_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INITP_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_00(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_01(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_02(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_03(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_04(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_05(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_06(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_07(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_08(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_09(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_0F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_10(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_11(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_12(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_13(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_14(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_15(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_16(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_17(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_18(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_19(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_1F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_20(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_21(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_22(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_23(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_24(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_25(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_26(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_27(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_28(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_29(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_2F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_30(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_31(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_32(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_33(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_34(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_35(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_36(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_37(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_38(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_39(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_3F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_40(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_41(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_42(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_43(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_44(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_45(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_46(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_47(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_48(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_49(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_4F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_50(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_51(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_52(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_53(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_54(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_55(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_56(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_57(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_58(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_59(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_5F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_60(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_61(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_62(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_63(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_64(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_65(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_66(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_67(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_68(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_69(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_6F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_70(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_71(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_72(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_73(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_74(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_75(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_76(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_77(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_78(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_79(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7A(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7B(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7C(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7D(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7E(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_7F(256'h0000000000000000000000000000000000000000000000000000000000000000),
    .INIT_A(36'h000000000),
    .INIT_B(36'h000000000),
    .INIT_FILE("NONE"),
    .IS_CLKARDCLK_INVERTED(1'b0),
    .IS_CLKBWRCLK_INVERTED(1'b0),
    .IS_ENARDEN_INVERTED(1'b0),
    .IS_ENBWREN_INVERTED(1'b0),
    .IS_RSTRAMARSTRAM_INVERTED(1'b0),
    .IS_RSTRAMB_INVERTED(1'b0),
    .IS_RSTREGARSTREG_INVERTED(1'b0),
    .IS_RSTREGB_INVERTED(1'b0),
    .RAM_EXTENSION_A("NONE"),
    .RAM_EXTENSION_B("NONE"),
    .RAM_MODE("TDP"),
    .RDADDR_COLLISION_HWCONFIG("DELAYED_WRITE"),
    .READ_WIDTH_A(18),
    .READ_WIDTH_B(18),
    .RSTREG_PRIORITY_A("RSTREG"),
    .RSTREG_PRIORITY_B("RSTREG"),
    .SIM_COLLISION_CHECK("ALL"),
    .SIM_DEVICE("7SERIES"),
    .SRVAL_A(36'h000000000),
    .SRVAL_B(36'h000000000),
    .WRITE_MODE_A("NO_CHANGE"),
    .WRITE_MODE_B("WRITE_FIRST"),
    .WRITE_WIDTH_A(18),
    .WRITE_WIDTH_B(18)) 
    \genblk5_0.bram36_tdp_bl.bram36_tdp_bl 
       (.ADDRARDADDR({1'b1,MIMTXWADDR,1'b1,1'b1,1'b1,1'b1}),
        .ADDRBWRADDR({1'b1,MIMTXRADDR,1'b1,1'b1,1'b1,1'b1}),
        .CASCADEINA(1'b0),
        .CASCADEINB(1'b0),
        .CASCADEOUTA(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTA_UNCONNECTED ),
        .CASCADEOUTB(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_CASCADEOUTB_UNCONNECTED ),
        .CLKARDCLK(pipe_userclk1_in),
        .CLKBWRCLK(pipe_userclk1_in),
        .DBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DBITERR_UNCONNECTED ),
        .DIADI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIADI_UNCONNECTED [31:16],wdata[16:9],wdata[7:0]}),
        .DIBDI({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DIBDI_UNCONNECTED [31:16],1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}),
        .DIPADIP({1'b0,1'b0,wdata[17],wdata[8]}),
        .DIPBDIP({1'b0,1'b0,1'b0,1'b0}),
        .DOADO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOADO_UNCONNECTED [31:16],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_20 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_21 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_22 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_23 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_24 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_25 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_26 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_27 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_28 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_29 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_30 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_31 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_32 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_33 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_34 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_35 }),
        .DOBDO({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOBDO_UNCONNECTED [31:16],rdata[16:9],rdata[7:0]}),
        .DOPADOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPADOP_UNCONNECTED [3:2],\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_70 ,\genblk5_0.bram36_tdp_bl.bram36_tdp_bl_n_71 }),
        .DOPBDOP({\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_DOPBDOP_UNCONNECTED [3:2],rdata[17],rdata[8]}),
        .ECCPARITY(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_ECCPARITY_UNCONNECTED [7:0]),
        .ENARDEN(mim_tx_wen),
        .ENBWREN(mim_tx_ren),
        .INJECTDBITERR(1'b0),
        .INJECTSBITERR(1'b0),
        .RDADDRECC(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_RDADDRECC_UNCONNECTED [8:0]),
        .REGCEAREGCE(1'b0),
        .REGCEB(1'b1),
        .RSTRAMARSTRAM(1'b0),
        .RSTRAMB(1'b0),
        .RSTREGARSTREG(1'b0),
        .RSTREGB(1'b0),
        .SBITERR(\NLW_genblk5_0.bram36_tdp_bl.bram36_tdp_bl_SBITERR_UNCONNECTED ),
        .WEA({1'b1,1'b1,1'b1,1'b1}),
        .WEBWE({1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0,1'b0}));
endmodule

(* DEST_SYNC_FF = "2" *) (* INIT_SYNC_FF = "0" *) (* ORIG_REF_NAME = "xpm_cdc_single" *) 
(* SIM_ASSERT_CHK = "0" *) (* SRC_INPUT_REG = "0" *) (* VERSION = "0" *) 
(* XPM_MODULE = "TRUE" *) (* keep_hierarchy = "true" *) (* xpm_cdc = "SINGLE" *) 
module pcie_7x_bridge_xpm_cdc_single
   (src_clk,
    src_in,
    dest_clk,
    dest_out);
  input src_clk;
  input src_in;
  input dest_clk;
  output dest_out;

  wire dest_clk;
  wire src_in;
  (* RTL_KEEP = "true" *) (* async_reg = "true" *) (* xpm_cdc = "SINGLE" *) wire [1:0]syncstages_ff;

  assign dest_out = syncstages_ff[1];
  (* ASYNC_REG *) 
  (* KEEP = "true" *) 
  (* XPM_CDC = "SINGLE" *) 
  FDRE \syncstages_ff_reg[0] 
       (.C(dest_clk),
        .CE(1'b1),
        .D(src_in),
        .Q(syncstages_ff[0]),
        .R(1'b0));
  (* ASYNC_REG *) 
  (* KEEP = "true" *) 
  (* XPM_CDC = "SINGLE" *) 
  FDRE \syncstages_ff_reg[1] 
       (.C(dest_clk),
        .CE(1'b1),
        .D(syncstages_ff[0]),
        .Q(syncstages_ff[1]),
        .R(1'b0));
endmodule

(* DEST_SYNC_FF = "2" *) (* INIT_SYNC_FF = "0" *) (* ORIG_REF_NAME = "xpm_cdc_single" *) 
(* SIM_ASSERT_CHK = "0" *) (* SRC_INPUT_REG = "0" *) (* VERSION = "0" *) 
(* XPM_MODULE = "TRUE" *) (* keep_hierarchy = "true" *) (* xpm_cdc = "SINGLE" *) 
module pcie_7x_bridge_xpm_cdc_single__2
   (src_clk,
    src_in,
    dest_clk,
    dest_out);
  input src_clk;
  input src_in;
  input dest_clk;
  output dest_out;

  wire dest_clk;
  wire src_in;
  (* RTL_KEEP = "true" *) (* async_reg = "true" *) (* xpm_cdc = "SINGLE" *) wire [1:0]syncstages_ff;

  assign dest_out = syncstages_ff[1];
  (* ASYNC_REG *) 
  (* KEEP = "true" *) 
  (* XPM_CDC = "SINGLE" *) 
  FDRE \syncstages_ff_reg[0] 
       (.C(dest_clk),
        .CE(1'b1),
        .D(src_in),
        .Q(syncstages_ff[0]),
        .R(1'b0));
  (* ASYNC_REG *) 
  (* KEEP = "true" *) 
  (* XPM_CDC = "SINGLE" *) 
  FDRE \syncstages_ff_reg[1] 
       (.C(dest_clk),
        .CE(1'b1),
        .D(syncstages_ff[0]),
        .Q(syncstages_ff[1]),
        .R(1'b0));
endmodule
`ifndef GLBL
`define GLBL
`timescale  1 ps / 1 ps

module glbl ();

    parameter ROC_WIDTH = 100000;
    parameter TOC_WIDTH = 0;
    parameter GRES_WIDTH = 10000;
    parameter GRES_START = 10000;

//--------   STARTUP Globals --------------
    wire GSR;
    wire GTS;
    wire GWE;
    wire PRLD;
    wire GRESTORE;
    tri1 p_up_tmp;
    tri (weak1, strong0) PLL_LOCKG = p_up_tmp;

    wire PROGB_GLBL;
    wire CCLKO_GLBL;
    wire FCSBO_GLBL;
    wire [3:0] DO_GLBL;
    wire [3:0] DI_GLBL;
   
    reg GSR_int;
    reg GTS_int;
    reg PRLD_int;
    reg GRESTORE_int;

//--------   JTAG Globals --------------
    wire JTAG_TDO_GLBL;
    wire JTAG_TCK_GLBL;
    wire JTAG_TDI_GLBL;
    wire JTAG_TMS_GLBL;
    wire JTAG_TRST_GLBL;

    reg JTAG_CAPTURE_GLBL;
    reg JTAG_RESET_GLBL;
    reg JTAG_SHIFT_GLBL;
    reg JTAG_UPDATE_GLBL;
    reg JTAG_RUNTEST_GLBL;

    reg JTAG_SEL1_GLBL = 0;
    reg JTAG_SEL2_GLBL = 0 ;
    reg JTAG_SEL3_GLBL = 0;
    reg JTAG_SEL4_GLBL = 0;

    reg JTAG_USER_TDO1_GLBL = 1'bz;
    reg JTAG_USER_TDO2_GLBL = 1'bz;
    reg JTAG_USER_TDO3_GLBL = 1'bz;
    reg JTAG_USER_TDO4_GLBL = 1'bz;

    assign (strong1, weak0) GSR = GSR_int;
    assign (strong1, weak0) GTS = GTS_int;
    assign (weak1, weak0) PRLD = PRLD_int;
    assign (strong1, weak0) GRESTORE = GRESTORE_int;

    initial begin
	GSR_int = 1'b1;
	PRLD_int = 1'b1;
	#(ROC_WIDTH)
	GSR_int = 1'b0;
	PRLD_int = 1'b0;
    end

    initial begin
	GTS_int = 1'b1;
	#(TOC_WIDTH)
	GTS_int = 1'b0;
    end

    initial begin 
	GRESTORE_int = 1'b0;
	#(GRES_START);
	GRESTORE_int = 1'b1;
	#(GRES_WIDTH);
	GRESTORE_int = 1'b0;
    end

endmodule
`endif
