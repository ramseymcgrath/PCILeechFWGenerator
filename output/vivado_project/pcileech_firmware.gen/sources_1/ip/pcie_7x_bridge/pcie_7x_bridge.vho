-- (c) Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
-- (c) Copyright 2022-2025 Advanced Micro Devices, Inc. All rights reserved.
-- 
-- This file contains confidential and proprietary information
-- of AMD and is protected under U.S. and international copyright
-- and other intellectual property laws.
-- 
-- DISCLAIMER
-- This disclaimer is not a license and does not grant any
-- rights to the materials distributed herewith. Except as
-- otherwise provided in a valid license issued to you by
-- AMD, and to the maximum extent permitted by applicable
-- law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
-- WITH ALL FAULTS, AND AMD HEREBY DISCLAIMS ALL WARRANTIES
-- AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
-- BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
-- INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
-- (2) AMD shall not be liable (whether in contract or tort,
-- including negligence, or under any other theory of
-- liability) for any loss or damage of any kind or nature
-- related to, arising under or in connection with these
-- materials, including for any direct, or any indirect,
-- special, incidental, or consequential loss or damage
-- (including loss of data, profits, goodwill, or any type of
-- loss or damage suffered as a result of any action brought
-- by a third party) even if such damage or loss was
-- reasonably foreseeable or AMD had been advised of the
-- possibility of the same.
-- 
-- CRITICAL APPLICATIONS
-- AMD products are not designed or intended to be fail-
-- safe, or for use in any application requiring fail-safe
-- performance, such as life-support or safety devices or
-- systems, Class III medical devices, nuclear facilities,
-- applications related to the deployment of airbags, or any
-- other applications that could lead to death, personal
-- injury, or severe property or environmental damage
-- (individually and collectively, "Critical
-- Applications"). Customer assumes the sole risk and
-- liability of any use of AMD products in Critical
-- Applications, subject only to applicable laws and
-- regulations governing limitations on product liability.
-- 
-- THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
-- PART OF THIS FILE AT ALL TIMES.
-- 
-- DO NOT MODIFY THIS FILE.
-- IP VLNV: xilinx.com:ip:pcie_7x:3.3
-- IP Revision: 22

-- The following code must appear in the VHDL architecture header.

------------- Begin Cut here for COMPONENT Declaration ------ COMP_TAG
COMPONENT pcie_7x_bridge
  PORT (
    pci_exp_txp : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    pci_exp_txn : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    pci_exp_rxp : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    pci_exp_rxn : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    pipe_pclk_in : IN STD_LOGIC;
    pipe_rxusrclk_in : IN STD_LOGIC;
    pipe_rxoutclk_in : IN STD_LOGIC_VECTOR(0 DOWNTO 0);
    pipe_dclk_in : IN STD_LOGIC;
    pipe_userclk1_in : IN STD_LOGIC;
    pipe_userclk2_in : IN STD_LOGIC;
    pipe_oobclk_in : IN STD_LOGIC;
    pipe_mmcm_lock_in : IN STD_LOGIC;
    pipe_txoutclk_out : OUT STD_LOGIC;
    pipe_rxoutclk_out : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    pipe_pclk_sel_out : OUT STD_LOGIC_VECTOR(0 DOWNTO 0);
    pipe_gen3_out : OUT STD_LOGIC;
    user_clk_out : OUT STD_LOGIC;
    user_reset_out : OUT STD_LOGIC;
    user_lnk_up : OUT STD_LOGIC;
    user_app_rdy : OUT STD_LOGIC;
    tx_buf_av : OUT STD_LOGIC_VECTOR(5 DOWNTO 0);
    tx_cfg_req : OUT STD_LOGIC;
    tx_err_drop : OUT STD_LOGIC;
    s_axis_tx_tready : OUT STD_LOGIC;
    s_axis_tx_tdata : IN STD_LOGIC_VECTOR(63 DOWNTO 0);
    s_axis_tx_tkeep : IN STD_LOGIC_VECTOR(7 DOWNTO 0);
    s_axis_tx_tlast : IN STD_LOGIC;
    s_axis_tx_tvalid : IN STD_LOGIC;
    s_axis_tx_tuser : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
    tx_cfg_gnt : IN STD_LOGIC;
    m_axis_rx_tdata : OUT STD_LOGIC_VECTOR(63 DOWNTO 0);
    m_axis_rx_tkeep : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    m_axis_rx_tlast : OUT STD_LOGIC;
    m_axis_rx_tvalid : OUT STD_LOGIC;
    m_axis_rx_tready : IN STD_LOGIC;
    m_axis_rx_tuser : OUT STD_LOGIC_VECTOR(21 DOWNTO 0);
    rx_np_ok : IN STD_LOGIC;
    rx_np_req : IN STD_LOGIC;
    fc_cpld : OUT STD_LOGIC_VECTOR(11 DOWNTO 0);
    fc_cplh : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    fc_npd : OUT STD_LOGIC_VECTOR(11 DOWNTO 0);
    fc_nph : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    fc_pd : OUT STD_LOGIC_VECTOR(11 DOWNTO 0);
    fc_ph : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    fc_sel : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
    cfg_mgmt_do : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
    cfg_mgmt_rd_wr_done : OUT STD_LOGIC;
    cfg_status : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_command : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_dstatus : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_dcommand : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_lstatus : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_lcommand : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_dcommand2 : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_pcie_link_state : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    cfg_pmcsr_pme_en : OUT STD_LOGIC;
    cfg_pmcsr_powerstate : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    cfg_pmcsr_pme_status : OUT STD_LOGIC;
    cfg_received_func_lvl_rst : OUT STD_LOGIC;
    cfg_mgmt_di : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
    cfg_mgmt_byte_en : IN STD_LOGIC_VECTOR(3 DOWNTO 0);
    cfg_mgmt_dwaddr : IN STD_LOGIC_VECTOR(9 DOWNTO 0);
    cfg_mgmt_wr_en : IN STD_LOGIC;
    cfg_mgmt_rd_en : IN STD_LOGIC;
    cfg_mgmt_wr_readonly : IN STD_LOGIC;
    cfg_err_ecrc : IN STD_LOGIC;
    cfg_err_ur : IN STD_LOGIC;
    cfg_err_cpl_timeout : IN STD_LOGIC;
    cfg_err_cpl_unexpect : IN STD_LOGIC;
    cfg_err_cpl_abort : IN STD_LOGIC;
    cfg_err_posted : IN STD_LOGIC;
    cfg_err_cor : IN STD_LOGIC;
    cfg_err_atomic_egress_blocked : IN STD_LOGIC;
    cfg_err_internal_cor : IN STD_LOGIC;
    cfg_err_malformed : IN STD_LOGIC;
    cfg_err_mc_blocked : IN STD_LOGIC;
    cfg_err_poisoned : IN STD_LOGIC;
    cfg_err_norecovery : IN STD_LOGIC;
    cfg_err_tlp_cpl_header : IN STD_LOGIC_VECTOR(47 DOWNTO 0);
    cfg_err_cpl_rdy : OUT STD_LOGIC;
    cfg_err_locked : IN STD_LOGIC;
    cfg_err_acs : IN STD_LOGIC;
    cfg_err_internal_uncor : IN STD_LOGIC;
    cfg_trn_pending : IN STD_LOGIC;
    cfg_pm_halt_aspm_l0s : IN STD_LOGIC;
    cfg_pm_halt_aspm_l1 : IN STD_LOGIC;
    cfg_pm_force_state_en : IN STD_LOGIC;
    cfg_pm_force_state : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
    cfg_dsn : IN STD_LOGIC_VECTOR(63 DOWNTO 0);
    cfg_interrupt : IN STD_LOGIC;
    cfg_interrupt_rdy : OUT STD_LOGIC;
    cfg_interrupt_assert : IN STD_LOGIC;
    cfg_interrupt_di : IN STD_LOGIC_VECTOR(7 DOWNTO 0);
    cfg_interrupt_do : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    cfg_interrupt_mmenable : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    cfg_interrupt_msienable : OUT STD_LOGIC;
    cfg_interrupt_msixenable : OUT STD_LOGIC;
    cfg_interrupt_msixfm : OUT STD_LOGIC;
    cfg_interrupt_stat : IN STD_LOGIC;
    cfg_pciecap_interrupt_msgnum : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
    cfg_to_turnoff : OUT STD_LOGIC;
    cfg_turnoff_ok : IN STD_LOGIC;
    cfg_bus_number : OUT STD_LOGIC_VECTOR(7 DOWNTO 0);
    cfg_device_number : OUT STD_LOGIC_VECTOR(4 DOWNTO 0);
    cfg_function_number : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    cfg_pm_wake : IN STD_LOGIC;
    cfg_pm_send_pme_to : IN STD_LOGIC;
    cfg_ds_bus_number : IN STD_LOGIC_VECTOR(7 DOWNTO 0);
    cfg_ds_device_number : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
    cfg_ds_function_number : IN STD_LOGIC_VECTOR(2 DOWNTO 0);
    cfg_mgmt_wr_rw1c_as_rw : IN STD_LOGIC;
    cfg_msg_received : OUT STD_LOGIC;
    cfg_msg_data : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    cfg_bridge_serr_en : OUT STD_LOGIC;
    cfg_slot_control_electromech_il_ctl_pulse : OUT STD_LOGIC;
    cfg_root_control_syserr_corr_err_en : OUT STD_LOGIC;
    cfg_root_control_syserr_non_fatal_err_en : OUT STD_LOGIC;
    cfg_root_control_syserr_fatal_err_en : OUT STD_LOGIC;
    cfg_root_control_pme_int_en : OUT STD_LOGIC;
    cfg_aer_rooterr_corr_err_reporting_en : OUT STD_LOGIC;
    cfg_aer_rooterr_non_fatal_err_reporting_en : OUT STD_LOGIC;
    cfg_aer_rooterr_fatal_err_reporting_en : OUT STD_LOGIC;
    cfg_aer_rooterr_corr_err_received : OUT STD_LOGIC;
    cfg_aer_rooterr_non_fatal_err_received : OUT STD_LOGIC;
    cfg_aer_rooterr_fatal_err_received : OUT STD_LOGIC;
    cfg_msg_received_err_cor : OUT STD_LOGIC;
    cfg_msg_received_err_non_fatal : OUT STD_LOGIC;
    cfg_msg_received_err_fatal : OUT STD_LOGIC;
    cfg_msg_received_pm_as_nak : OUT STD_LOGIC;
    cfg_msg_received_pm_pme : OUT STD_LOGIC;
    cfg_msg_received_pme_to_ack : OUT STD_LOGIC;
    cfg_msg_received_assert_int_a : OUT STD_LOGIC;
    cfg_msg_received_assert_int_b : OUT STD_LOGIC;
    cfg_msg_received_assert_int_c : OUT STD_LOGIC;
    cfg_msg_received_assert_int_d : OUT STD_LOGIC;
    cfg_msg_received_deassert_int_a : OUT STD_LOGIC;
    cfg_msg_received_deassert_int_b : OUT STD_LOGIC;
    cfg_msg_received_deassert_int_c : OUT STD_LOGIC;
    cfg_msg_received_deassert_int_d : OUT STD_LOGIC;
    cfg_msg_received_setslotpowerlimit : OUT STD_LOGIC;
    pl_directed_link_change : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
    pl_directed_link_width : IN STD_LOGIC_VECTOR(1 DOWNTO 0);
    pl_directed_link_speed : IN STD_LOGIC;
    pl_directed_link_auton : IN STD_LOGIC;
    pl_upstream_prefer_deemph : IN STD_LOGIC;
    pl_sel_lnk_rate : OUT STD_LOGIC;
    pl_sel_lnk_width : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    pl_ltssm_state : OUT STD_LOGIC_VECTOR(5 DOWNTO 0);
    pl_lane_reversal_mode : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    pl_phy_lnk_up : OUT STD_LOGIC;
    pl_tx_pm_state : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    pl_rx_pm_state : OUT STD_LOGIC_VECTOR(1 DOWNTO 0);
    pl_link_upcfg_cap : OUT STD_LOGIC;
    pl_link_gen2_cap : OUT STD_LOGIC;
    pl_link_partner_gen2_supported : OUT STD_LOGIC;
    pl_initial_link_width : OUT STD_LOGIC_VECTOR(2 DOWNTO 0);
    pl_directed_change_done : OUT STD_LOGIC;
    pl_received_hot_rst : OUT STD_LOGIC;
    pl_transmit_hot_rst : IN STD_LOGIC;
    pl_downstream_deemph_source : IN STD_LOGIC;
    cfg_err_aer_headerlog : IN STD_LOGIC_VECTOR(127 DOWNTO 0);
    cfg_aer_interrupt_msgnum : IN STD_LOGIC_VECTOR(4 DOWNTO 0);
    cfg_err_aer_headerlog_set : OUT STD_LOGIC;
    cfg_aer_ecrc_check_en : OUT STD_LOGIC;
    cfg_aer_ecrc_gen_en : OUT STD_LOGIC;
    cfg_vc_tcvc_map : OUT STD_LOGIC_VECTOR(6 DOWNTO 0);
    sys_clk : IN STD_LOGIC;
    sys_rst_n : IN STD_LOGIC;
    pipe_mmcm_rst_n : IN STD_LOGIC;
    pcie_drp_clk : IN STD_LOGIC;
    pcie_drp_en : IN STD_LOGIC;
    pcie_drp_we : IN STD_LOGIC;
    pcie_drp_addr : IN STD_LOGIC_VECTOR(8 DOWNTO 0);
    pcie_drp_di : IN STD_LOGIC_VECTOR(15 DOWNTO 0);
    pcie_drp_do : OUT STD_LOGIC_VECTOR(15 DOWNTO 0);
    pcie_drp_rdy : OUT STD_LOGIC 
  );
END COMPONENT;
-- COMP_TAG_END ------ End COMPONENT Declaration ------------

-- The following code must appear in the VHDL architecture
-- body. Substitute your own instance name and net names.

------------- Begin Cut here for INSTANTIATION Template ----- INST_TAG
your_instance_name : pcie_7x_bridge
  PORT MAP (
    pci_exp_txp => pci_exp_txp,
    pci_exp_txn => pci_exp_txn,
    pci_exp_rxp => pci_exp_rxp,
    pci_exp_rxn => pci_exp_rxn,
    pipe_pclk_in => pipe_pclk_in,
    pipe_rxusrclk_in => pipe_rxusrclk_in,
    pipe_rxoutclk_in => pipe_rxoutclk_in,
    pipe_dclk_in => pipe_dclk_in,
    pipe_userclk1_in => pipe_userclk1_in,
    pipe_userclk2_in => pipe_userclk2_in,
    pipe_oobclk_in => pipe_oobclk_in,
    pipe_mmcm_lock_in => pipe_mmcm_lock_in,
    pipe_txoutclk_out => pipe_txoutclk_out,
    pipe_rxoutclk_out => pipe_rxoutclk_out,
    pipe_pclk_sel_out => pipe_pclk_sel_out,
    pipe_gen3_out => pipe_gen3_out,
    user_clk_out => user_clk_out,
    user_reset_out => user_reset_out,
    user_lnk_up => user_lnk_up,
    user_app_rdy => user_app_rdy,
    tx_buf_av => tx_buf_av,
    tx_cfg_req => tx_cfg_req,
    tx_err_drop => tx_err_drop,
    s_axis_tx_tready => s_axis_tx_tready,
    s_axis_tx_tdata => s_axis_tx_tdata,
    s_axis_tx_tkeep => s_axis_tx_tkeep,
    s_axis_tx_tlast => s_axis_tx_tlast,
    s_axis_tx_tvalid => s_axis_tx_tvalid,
    s_axis_tx_tuser => s_axis_tx_tuser,
    tx_cfg_gnt => tx_cfg_gnt,
    m_axis_rx_tdata => m_axis_rx_tdata,
    m_axis_rx_tkeep => m_axis_rx_tkeep,
    m_axis_rx_tlast => m_axis_rx_tlast,
    m_axis_rx_tvalid => m_axis_rx_tvalid,
    m_axis_rx_tready => m_axis_rx_tready,
    m_axis_rx_tuser => m_axis_rx_tuser,
    rx_np_ok => rx_np_ok,
    rx_np_req => rx_np_req,
    fc_cpld => fc_cpld,
    fc_cplh => fc_cplh,
    fc_npd => fc_npd,
    fc_nph => fc_nph,
    fc_pd => fc_pd,
    fc_ph => fc_ph,
    fc_sel => fc_sel,
    cfg_mgmt_do => cfg_mgmt_do,
    cfg_mgmt_rd_wr_done => cfg_mgmt_rd_wr_done,
    cfg_status => cfg_status,
    cfg_command => cfg_command,
    cfg_dstatus => cfg_dstatus,
    cfg_dcommand => cfg_dcommand,
    cfg_lstatus => cfg_lstatus,
    cfg_lcommand => cfg_lcommand,
    cfg_dcommand2 => cfg_dcommand2,
    cfg_pcie_link_state => cfg_pcie_link_state,
    cfg_pmcsr_pme_en => cfg_pmcsr_pme_en,
    cfg_pmcsr_powerstate => cfg_pmcsr_powerstate,
    cfg_pmcsr_pme_status => cfg_pmcsr_pme_status,
    cfg_received_func_lvl_rst => cfg_received_func_lvl_rst,
    cfg_mgmt_di => cfg_mgmt_di,
    cfg_mgmt_byte_en => cfg_mgmt_byte_en,
    cfg_mgmt_dwaddr => cfg_mgmt_dwaddr,
    cfg_mgmt_wr_en => cfg_mgmt_wr_en,
    cfg_mgmt_rd_en => cfg_mgmt_rd_en,
    cfg_mgmt_wr_readonly => cfg_mgmt_wr_readonly,
    cfg_err_ecrc => cfg_err_ecrc,
    cfg_err_ur => cfg_err_ur,
    cfg_err_cpl_timeout => cfg_err_cpl_timeout,
    cfg_err_cpl_unexpect => cfg_err_cpl_unexpect,
    cfg_err_cpl_abort => cfg_err_cpl_abort,
    cfg_err_posted => cfg_err_posted,
    cfg_err_cor => cfg_err_cor,
    cfg_err_atomic_egress_blocked => cfg_err_atomic_egress_blocked,
    cfg_err_internal_cor => cfg_err_internal_cor,
    cfg_err_malformed => cfg_err_malformed,
    cfg_err_mc_blocked => cfg_err_mc_blocked,
    cfg_err_poisoned => cfg_err_poisoned,
    cfg_err_norecovery => cfg_err_norecovery,
    cfg_err_tlp_cpl_header => cfg_err_tlp_cpl_header,
    cfg_err_cpl_rdy => cfg_err_cpl_rdy,
    cfg_err_locked => cfg_err_locked,
    cfg_err_acs => cfg_err_acs,
    cfg_err_internal_uncor => cfg_err_internal_uncor,
    cfg_trn_pending => cfg_trn_pending,
    cfg_pm_halt_aspm_l0s => cfg_pm_halt_aspm_l0s,
    cfg_pm_halt_aspm_l1 => cfg_pm_halt_aspm_l1,
    cfg_pm_force_state_en => cfg_pm_force_state_en,
    cfg_pm_force_state => cfg_pm_force_state,
    cfg_dsn => cfg_dsn,
    cfg_interrupt => cfg_interrupt,
    cfg_interrupt_rdy => cfg_interrupt_rdy,
    cfg_interrupt_assert => cfg_interrupt_assert,
    cfg_interrupt_di => cfg_interrupt_di,
    cfg_interrupt_do => cfg_interrupt_do,
    cfg_interrupt_mmenable => cfg_interrupt_mmenable,
    cfg_interrupt_msienable => cfg_interrupt_msienable,
    cfg_interrupt_msixenable => cfg_interrupt_msixenable,
    cfg_interrupt_msixfm => cfg_interrupt_msixfm,
    cfg_interrupt_stat => cfg_interrupt_stat,
    cfg_pciecap_interrupt_msgnum => cfg_pciecap_interrupt_msgnum,
    cfg_to_turnoff => cfg_to_turnoff,
    cfg_turnoff_ok => cfg_turnoff_ok,
    cfg_bus_number => cfg_bus_number,
    cfg_device_number => cfg_device_number,
    cfg_function_number => cfg_function_number,
    cfg_pm_wake => cfg_pm_wake,
    cfg_pm_send_pme_to => cfg_pm_send_pme_to,
    cfg_ds_bus_number => cfg_ds_bus_number,
    cfg_ds_device_number => cfg_ds_device_number,
    cfg_ds_function_number => cfg_ds_function_number,
    cfg_mgmt_wr_rw1c_as_rw => cfg_mgmt_wr_rw1c_as_rw,
    cfg_msg_received => cfg_msg_received,
    cfg_msg_data => cfg_msg_data,
    cfg_bridge_serr_en => cfg_bridge_serr_en,
    cfg_slot_control_electromech_il_ctl_pulse => cfg_slot_control_electromech_il_ctl_pulse,
    cfg_root_control_syserr_corr_err_en => cfg_root_control_syserr_corr_err_en,
    cfg_root_control_syserr_non_fatal_err_en => cfg_root_control_syserr_non_fatal_err_en,
    cfg_root_control_syserr_fatal_err_en => cfg_root_control_syserr_fatal_err_en,
    cfg_root_control_pme_int_en => cfg_root_control_pme_int_en,
    cfg_aer_rooterr_corr_err_reporting_en => cfg_aer_rooterr_corr_err_reporting_en,
    cfg_aer_rooterr_non_fatal_err_reporting_en => cfg_aer_rooterr_non_fatal_err_reporting_en,
    cfg_aer_rooterr_fatal_err_reporting_en => cfg_aer_rooterr_fatal_err_reporting_en,
    cfg_aer_rooterr_corr_err_received => cfg_aer_rooterr_corr_err_received,
    cfg_aer_rooterr_non_fatal_err_received => cfg_aer_rooterr_non_fatal_err_received,
    cfg_aer_rooterr_fatal_err_received => cfg_aer_rooterr_fatal_err_received,
    cfg_msg_received_err_cor => cfg_msg_received_err_cor,
    cfg_msg_received_err_non_fatal => cfg_msg_received_err_non_fatal,
    cfg_msg_received_err_fatal => cfg_msg_received_err_fatal,
    cfg_msg_received_pm_as_nak => cfg_msg_received_pm_as_nak,
    cfg_msg_received_pm_pme => cfg_msg_received_pm_pme,
    cfg_msg_received_pme_to_ack => cfg_msg_received_pme_to_ack,
    cfg_msg_received_assert_int_a => cfg_msg_received_assert_int_a,
    cfg_msg_received_assert_int_b => cfg_msg_received_assert_int_b,
    cfg_msg_received_assert_int_c => cfg_msg_received_assert_int_c,
    cfg_msg_received_assert_int_d => cfg_msg_received_assert_int_d,
    cfg_msg_received_deassert_int_a => cfg_msg_received_deassert_int_a,
    cfg_msg_received_deassert_int_b => cfg_msg_received_deassert_int_b,
    cfg_msg_received_deassert_int_c => cfg_msg_received_deassert_int_c,
    cfg_msg_received_deassert_int_d => cfg_msg_received_deassert_int_d,
    cfg_msg_received_setslotpowerlimit => cfg_msg_received_setslotpowerlimit,
    pl_directed_link_change => pl_directed_link_change,
    pl_directed_link_width => pl_directed_link_width,
    pl_directed_link_speed => pl_directed_link_speed,
    pl_directed_link_auton => pl_directed_link_auton,
    pl_upstream_prefer_deemph => pl_upstream_prefer_deemph,
    pl_sel_lnk_rate => pl_sel_lnk_rate,
    pl_sel_lnk_width => pl_sel_lnk_width,
    pl_ltssm_state => pl_ltssm_state,
    pl_lane_reversal_mode => pl_lane_reversal_mode,
    pl_phy_lnk_up => pl_phy_lnk_up,
    pl_tx_pm_state => pl_tx_pm_state,
    pl_rx_pm_state => pl_rx_pm_state,
    pl_link_upcfg_cap => pl_link_upcfg_cap,
    pl_link_gen2_cap => pl_link_gen2_cap,
    pl_link_partner_gen2_supported => pl_link_partner_gen2_supported,
    pl_initial_link_width => pl_initial_link_width,
    pl_directed_change_done => pl_directed_change_done,
    pl_received_hot_rst => pl_received_hot_rst,
    pl_transmit_hot_rst => pl_transmit_hot_rst,
    pl_downstream_deemph_source => pl_downstream_deemph_source,
    cfg_err_aer_headerlog => cfg_err_aer_headerlog,
    cfg_aer_interrupt_msgnum => cfg_aer_interrupt_msgnum,
    cfg_err_aer_headerlog_set => cfg_err_aer_headerlog_set,
    cfg_aer_ecrc_check_en => cfg_aer_ecrc_check_en,
    cfg_aer_ecrc_gen_en => cfg_aer_ecrc_gen_en,
    cfg_vc_tcvc_map => cfg_vc_tcvc_map,
    sys_clk => sys_clk,
    sys_rst_n => sys_rst_n,
    pipe_mmcm_rst_n => pipe_mmcm_rst_n,
    pcie_drp_clk => pcie_drp_clk,
    pcie_drp_en => pcie_drp_en,
    pcie_drp_we => pcie_drp_we,
    pcie_drp_addr => pcie_drp_addr,
    pcie_drp_di => pcie_drp_di,
    pcie_drp_do => pcie_drp_do,
    pcie_drp_rdy => pcie_drp_rdy
  );
-- INST_TAG_END ------ End INSTANTIATION Template ---------

-- You must compile the wrapper file pcie_7x_bridge.vhd when simulating
-- the core, pcie_7x_bridge. When compiling the wrapper file, be sure to
-- reference the VHDL simulation library.



