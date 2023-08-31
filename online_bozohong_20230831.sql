/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80100 (8.1.0)
 Source Host           : 172.19.156.52:40004
 Source Schema         : online

 Target Server Type    : MySQL
 Target Server Version : 80100 (8.1.0)
 File Encoding         : 65001

 Date: 31/08/2023 15:03:53
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app_configuration
-- ----------------------------
DROP TABLE IF EXISTS `app_configuration`;
CREATE TABLE `app_configuration`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of app_configuration
-- ----------------------------
INSERT INTO `app_configuration` VALUES (1, 'tempdir', '/tmp/wtbonline');
INSERT INTO `app_configuration` VALUES (2, 'report_outpath', '/var/local/wtbonline/report');
INSERT INTO `app_configuration` VALUES (3, 'model_path', '/var/local/wtbonline/model');
INSERT INTO `app_configuration` VALUES (4, 'log_path', '/var/local/wtbonline/log');

-- ----------------------------
-- Table structure for app_server
-- ----------------------------
DROP TABLE IF EXISTS `app_server`;
CREATE TABLE `app_server`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `host` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `remote` int NULL DEFAULT NULL,
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `port` int NULL DEFAULT NULL,
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `database` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of app_server
-- ----------------------------
INSERT INTO `app_server` VALUES (1, 'tdengine', '192.168.0.6', 1, 'restapi', 6041, 'root', 'gAAAAABk1OpyQl28ffKF6SosFzNjiyF6fKHO-Yy0D8UEEbK8Z9oKcsfsfabTTjWcIz_A2ZbjK6XmoQVNEsS71ThLriL0NF6m8A==', 'scada');
INSERT INTO `app_server` VALUES (2, 'tdengine', 'taos', 0, 'native', 6030, 'root', 'gAAAAABk1OpyQl28ffKF6SosFzNjiyF6fKHO-Yy0D8UEEbK8Z9oKcsfsfabTTjWcIz_A2ZbjK6XmoQVNEsS71ThLriL0NF6m8A==', 'windfarm');

-- ----------------------------
-- Table structure for model
-- ----------------------------
DROP TABLE IF EXISTS `model`;
CREATE TABLE `model`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `farm_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的set_id对应',
  `turbine_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的sdevice对应',
  `uuid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模型唯一码',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模型类型',
  `start_time` datetime NOT NULL COMMENT '建模数据起始时间',
  `end_time` datetime NOT NULL COMMENT '建模数据结束时间',
  `is_local` int NOT NULL DEFAULT 1 COMMENT '1=利用本地数据训练得到的模型',
  `create_time` datetime NOT NULL COMMENT '本记录生成时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uuid`(`uuid` ASC) USING BTREE,
  UNIQUE INDEX `compoud`(`set_id` ASC, `turbine_id` ASC, `name` ASC, `create_time` ASC) USING BTREE,
  INDEX `turbine_id`(`turbine_id` ASC) USING BTREE,
  CONSTRAINT `model_ibfk_1` FOREIGN KEY (`set_id`, `turbine_id`) REFERENCES `windfarm_configuration` (`set_id`, `turbine_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model
-- ----------------------------

-- ----------------------------
-- Table structure for model_anormaly
-- ----------------------------
DROP TABLE IF EXISTS `model_anormaly`;
CREATE TABLE `model_anormaly`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `turbine_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sample_id` int NOT NULL,
  `bin` datetime NOT NULL,
  `model_uuid` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE,
  INDEX `turbine_id`(`turbine_id` ASC) USING BTREE,
  INDEX `sample_id`(`sample_id` ASC) USING BTREE,
  INDEX `set_id_2`(`set_id` ASC, `turbine_id` ASC) USING BTREE,
  CONSTRAINT `model_anormaly_ibfk_4` FOREIGN KEY (`set_id`, `turbine_id`) REFERENCES `windfarm_configuration` (`set_id`, `turbine_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 77 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_anormaly
-- ----------------------------

-- ----------------------------
-- Table structure for model_label
-- ----------------------------
DROP TABLE IF EXISTS `model_label`;
CREATE TABLE `model_label`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `turbine_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sample_id` int NOT NULL,
  `bin` datetime NOT NULL,
  `is_anormaly` int NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE,
  INDEX `set_id_3`(`set_id` ASC, `turbine_id` ASC) USING BTREE,
  INDEX `turbine_id_1`(`turbine_id` ASC) USING BTREE,
  INDEX `sample_id`(`sample_id` ASC) USING BTREE,
  CONSTRAINT `set_id_3` FOREIGN KEY (`set_id`, `turbine_id`) REFERENCES `windfarm_configuration` (`set_id`, `turbine_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `username` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_label
-- ----------------------------

-- ----------------------------
-- Table structure for statistics_sample
-- ----------------------------
DROP TABLE IF EXISTS `statistics_sample`;
CREATE TABLE `statistics_sample`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `turbine_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `bin` datetime NOT NULL,
  `var_101_mean` float NULL DEFAULT NULL,
  `var_101_rms` float NULL DEFAULT NULL,
  `var_101_iqr` float NULL DEFAULT NULL,
  `var_101_std` float NULL DEFAULT NULL,
  `var_101_skew` float NULL DEFAULT NULL,
  `var_101_kurt` float NULL DEFAULT NULL,
  `var_101_wf` float NULL DEFAULT NULL,
  `var_101_crest` float NULL DEFAULT NULL,
  `var_101_zc` float NULL DEFAULT NULL,
  `var_101_cv` float NULL DEFAULT NULL,
  `var_101_imp` float NULL DEFAULT NULL,
  `var_102_mean` float NULL DEFAULT NULL,
  `var_102_rms` float NULL DEFAULT NULL,
  `var_102_iqr` float NULL DEFAULT NULL,
  `var_102_std` float NULL DEFAULT NULL,
  `var_102_skew` float NULL DEFAULT NULL,
  `var_102_kurt` float NULL DEFAULT NULL,
  `var_102_wf` float NULL DEFAULT NULL,
  `var_102_crest` float NULL DEFAULT NULL,
  `var_102_zc` float NULL DEFAULT NULL,
  `var_102_cv` float NULL DEFAULT NULL,
  `var_102_imp` float NULL DEFAULT NULL,
  `var_103_mean` float NULL DEFAULT NULL,
  `var_103_rms` float NULL DEFAULT NULL,
  `var_103_iqr` float NULL DEFAULT NULL,
  `var_103_std` float NULL DEFAULT NULL,
  `var_103_skew` float NULL DEFAULT NULL,
  `var_103_kurt` float NULL DEFAULT NULL,
  `var_103_wf` float NULL DEFAULT NULL,
  `var_103_crest` float NULL DEFAULT NULL,
  `var_103_zc` float NULL DEFAULT NULL,
  `var_103_cv` float NULL DEFAULT NULL,
  `var_103_imp` float NULL DEFAULT NULL,
  `var_226_mean` float NULL DEFAULT NULL,
  `var_226_rms` float NULL DEFAULT NULL,
  `var_226_iqr` float NULL DEFAULT NULL,
  `var_226_std` float NULL DEFAULT NULL,
  `var_226_skew` float NULL DEFAULT NULL,
  `var_226_kurt` float NULL DEFAULT NULL,
  `var_226_wf` float NULL DEFAULT NULL,
  `var_226_crest` float NULL DEFAULT NULL,
  `var_226_zc` float NULL DEFAULT NULL,
  `var_226_cv` float NULL DEFAULT NULL,
  `var_226_imp` float NULL DEFAULT NULL,
  `var_246_mean` float NULL DEFAULT NULL,
  `var_246_rms` float NULL DEFAULT NULL,
  `var_246_iqr` float NULL DEFAULT NULL,
  `var_246_std` float NULL DEFAULT NULL,
  `var_246_skew` float NULL DEFAULT NULL,
  `var_246_kurt` float NULL DEFAULT NULL,
  `var_246_wf` float NULL DEFAULT NULL,
  `var_246_crest` float NULL DEFAULT NULL,
  `var_246_zc` float NULL DEFAULT NULL,
  `var_246_cv` float NULL DEFAULT NULL,
  `var_246_imp` float NULL DEFAULT NULL,
  `var_2709_mean` float NULL DEFAULT NULL,
  `var_2709_rms` float NULL DEFAULT NULL,
  `var_2709_iqr` float NULL DEFAULT NULL,
  `var_2709_std` float NULL DEFAULT NULL,
  `var_2709_skew` float NULL DEFAULT NULL,
  `var_2709_kurt` float NULL DEFAULT NULL,
  `var_2709_wf` float NULL DEFAULT NULL,
  `var_2709_crest` float NULL DEFAULT NULL,
  `var_2709_zc` float NULL DEFAULT NULL,
  `var_2709_cv` float NULL DEFAULT NULL,
  `var_2709_imp` float NULL DEFAULT NULL,
  `var_355_mean` float NULL DEFAULT NULL,
  `var_355_rms` float NULL DEFAULT NULL,
  `var_355_iqr` float NULL DEFAULT NULL,
  `var_355_std` float NULL DEFAULT NULL,
  `var_355_skew` float NULL DEFAULT NULL,
  `var_355_kurt` float NULL DEFAULT NULL,
  `var_355_wf` float NULL DEFAULT NULL,
  `var_355_crest` float NULL DEFAULT NULL,
  `var_355_zc` float NULL DEFAULT NULL,
  `var_355_cv` float NULL DEFAULT NULL,
  `var_355_imp` float NULL DEFAULT NULL,
  `var_356_mean` float NULL DEFAULT NULL,
  `var_356_rms` float NULL DEFAULT NULL,
  `var_356_iqr` float NULL DEFAULT NULL,
  `var_356_std` float NULL DEFAULT NULL,
  `var_356_skew` float NULL DEFAULT NULL,
  `var_356_kurt` float NULL DEFAULT NULL,
  `var_356_wf` float NULL DEFAULT NULL,
  `var_356_crest` float NULL DEFAULT NULL,
  `var_356_zc` float NULL DEFAULT NULL,
  `var_356_cv` float NULL DEFAULT NULL,
  `var_356_imp` float NULL DEFAULT NULL,
  `evntemp_mean` float NULL DEFAULT NULL,
  `evntemp_rms` float NULL DEFAULT NULL,
  `evntemp_iqr` float NULL DEFAULT NULL,
  `evntemp_std` float NULL DEFAULT NULL,
  `evntemp_skew` float NULL DEFAULT NULL,
  `evntemp_kurt` float NULL DEFAULT NULL,
  `evntemp_wf` float NULL DEFAULT NULL,
  `evntemp_crest` float NULL DEFAULT NULL,
  `evntemp_zc` float NULL DEFAULT NULL,
  `evntemp_cv` float NULL DEFAULT NULL,
  `evntemp_imp` float NULL DEFAULT NULL,
  `var_372_mean` float NULL DEFAULT NULL,
  `var_372_rms` float NULL DEFAULT NULL,
  `var_372_iqr` float NULL DEFAULT NULL,
  `var_372_std` float NULL DEFAULT NULL,
  `var_372_skew` float NULL DEFAULT NULL,
  `var_372_kurt` float NULL DEFAULT NULL,
  `var_372_wf` float NULL DEFAULT NULL,
  `var_372_crest` float NULL DEFAULT NULL,
  `var_372_zc` float NULL DEFAULT NULL,
  `var_372_cv` float NULL DEFAULT NULL,
  `var_372_imp` float NULL DEFAULT NULL,
  `var_382_mean` float NULL DEFAULT NULL,
  `var_382_rms` float NULL DEFAULT NULL,
  `var_382_iqr` float NULL DEFAULT NULL,
  `var_382_std` float NULL DEFAULT NULL,
  `var_382_skew` float NULL DEFAULT NULL,
  `var_382_kurt` float NULL DEFAULT NULL,
  `var_382_wf` float NULL DEFAULT NULL,
  `var_382_crest` float NULL DEFAULT NULL,
  `var_382_zc` float NULL DEFAULT NULL,
  `var_382_cv` float NULL DEFAULT NULL,
  `var_382_imp` float NULL DEFAULT NULL,
  `var_383_mean` float NULL DEFAULT NULL,
  `var_383_rms` float NULL DEFAULT NULL,
  `var_383_iqr` float NULL DEFAULT NULL,
  `var_383_std` float NULL DEFAULT NULL,
  `var_383_skew` float NULL DEFAULT NULL,
  `var_383_kurt` float NULL DEFAULT NULL,
  `var_383_wf` float NULL DEFAULT NULL,
  `var_383_crest` float NULL DEFAULT NULL,
  `var_383_zc` float NULL DEFAULT NULL,
  `var_383_cv` float NULL DEFAULT NULL,
  `var_383_imp` float NULL DEFAULT NULL,
  `var_409_mean` float NULL DEFAULT NULL,
  `var_409_rms` float NULL DEFAULT NULL,
  `var_409_iqr` float NULL DEFAULT NULL,
  `var_409_std` float NULL DEFAULT NULL,
  `var_409_skew` float NULL DEFAULT NULL,
  `var_409_kurt` float NULL DEFAULT NULL,
  `var_409_wf` float NULL DEFAULT NULL,
  `var_409_crest` float NULL DEFAULT NULL,
  `var_409_zc` float NULL DEFAULT NULL,
  `var_409_cv` float NULL DEFAULT NULL,
  `var_409_imp` float NULL DEFAULT NULL,
  `var_94_mean` float NULL DEFAULT NULL,
  `var_94_rms` float NULL DEFAULT NULL,
  `var_94_iqr` float NULL DEFAULT NULL,
  `var_94_std` float NULL DEFAULT NULL,
  `var_94_skew` float NULL DEFAULT NULL,
  `var_94_kurt` float NULL DEFAULT NULL,
  `var_94_wf` float NULL DEFAULT NULL,
  `var_94_crest` float NULL DEFAULT NULL,
  `var_94_zc` float NULL DEFAULT NULL,
  `var_94_cv` float NULL DEFAULT NULL,
  `var_94_imp` float NULL DEFAULT NULL,
  `ongrid_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ongrid_unique` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ongrid_nunique` int NULL DEFAULT NULL,
  `limitpowbool_mode` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `limitpowbool_unique` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `limitpowbool_nunique` int NULL DEFAULT NULL,
  `workmode_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `workmode_unique` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `workmode_nunique` int NULL DEFAULT NULL,
  `totalfaultbool_mode` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `totalfaultbool_unique` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `totalfaultbool_nunique` int NULL DEFAULT NULL,
  `nobs` float NULL DEFAULT NULL,
  `validation` float NULL DEFAULT NULL,
  `pv_c` float NULL DEFAULT NULL,
  `pv_t` float NULL DEFAULT NULL,
  `pv_ctt` float NULL DEFAULT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `a`(`set_id` ASC, `turbine_id` ASC, `bin` ASC, `create_time` ASC) USING BTREE,
  INDEX `ix_statistics_sample_bin`(`bin` ASC) USING BTREE,
  INDEX `ix_statistics_sample_turbine_id`(`turbine_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of statistics_sample
-- ----------------------------

-- ----------------------------
-- Table structure for timed_task_log
-- ----------------------------
DROP TABLE IF EXISTS `timed_task_log`;
CREATE TABLE `timed_task_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `success` int NOT NULL,
  `func` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `args` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `kwargs` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `pid` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of timed_task_log
-- ----------------------------
INSERT INTO `timed_task_log` VALUES (3, 0, 'update_tsdb', '', '{}', '2023-08-29 09:17:00', '2023-08-29 09:17:03', 7);
INSERT INTO `timed_task_log` VALUES (4, 0, 'update_tsdb', '', '{}', '2023-08-29 09:18:00', '2023-08-29 09:18:03', 7);
INSERT INTO `timed_task_log` VALUES (5, 0, 'update_tsdb', '', '{}', '2023-08-29 11:35:00', '2023-08-29 11:35:03', 7);
INSERT INTO `timed_task_log` VALUES (6, 1, 'update_tsdb', '', '{}', '2023-08-29 11:37:06', '2023-08-29 12:02:16', 7);
INSERT INTO `timed_task_log` VALUES (7, 1, 'init_tdengine', '', '{}', '2023-08-29 13:56:08', '2023-08-29 13:56:08', 284);
INSERT INTO `timed_task_log` VALUES (8, 1, 'update_statistic_sample', '', '{}', '2023-08-29 19:38:00', '2023-08-29 20:02:55', 8);
INSERT INTO `timed_task_log` VALUES (9, 1, 'train_all', '', '{\'start_time\': \'2023-05-01 00:00:00\', \'end_time\': \'2023-08-15 00:00:00\', \'minimum\': 3000}', '2023-08-30 07:33:26', '2023-08-30 07:33:30', 8);
INSERT INTO `timed_task_log` VALUES (10, 1, 'predict_all', '', '{\'start_time\': \'2023-05-01 00:00:00\', \'end_time\': \'2023-08-15 00:00:00\', \'size\': 20}', '2023-08-30 07:34:26', '2023-08-30 07:34:30', 7);
INSERT INTO `timed_task_log` VALUES (11, 1, 'build_brief_report_all', '', '{\'end_time\': \'2023-08-01 00:00:00\', \'delta\': 60}', '2023-08-30 07:38:05', '2023-08-30 07:38:24', 7);
INSERT INTO `timed_task_log` VALUES (12, 1, 'build_brief_report_all', '', '{\'end_time\': \'2023-08-01 00:00:00\', \'delta\': 60}', '2023-08-30 07:46:45', '2023-08-30 07:47:03', 7);

-- ----------------------------
-- Table structure for turbine_model_points
-- ----------------------------
DROP TABLE IF EXISTS `turbine_model_points`;
CREATE TABLE `turbine_model_points`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `select` int NOT NULL DEFAULT 0 COMMENT '1=采集到本地tdengine',
  `stat_operation` int NOT NULL DEFAULT 0 COMMENT '1=用于计算statistics_operation表的字段',
  `stat_sample` int NOT NULL DEFAULT 0 COMMENT '1=用于计算statistics_sample表的字段',
  `stat_accumulation` int NOT NULL DEFAULT 0 COMMENT '1=用于计算statistics_accumluation表的字段',
  `point_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `var_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '本地tdengine，set_id=20835的var_name，不变量',
  `datatype` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ref_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '远程tdengine的变量名，按需修改',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE,
  CONSTRAINT `turbine_model_points_ibfk_1` FOREIGN KEY (`set_id`) REFERENCES `windfarm_infomation` (`set_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 3059 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_model_points
-- ----------------------------
INSERT INTO `turbine_model_points` VALUES (1, '20835', 0, 0, 0, 0, '机组总体故障状态', 'var_23132', 'B', 'notdefined', 'var_23132');
INSERT INTO `turbine_model_points` VALUES (2, '20835', 0, 0, 0, 0, '远方就地控制开关', 'var_23133', 'B', 'notdefined', 'var_23133');
INSERT INTO `turbine_model_points` VALUES (3, '20835', 0, 0, 0, 0, '机组自身限功率运行状态', 'var_23134', 'B', 'notdefined', 'var_23134');
INSERT INTO `turbine_model_points` VALUES (4, '20835', 0, 0, 0, 0, '就地限功率运行状态', 'var_23135', 'B', 'notdefined', 'var_23135');
INSERT INTO `turbine_model_points` VALUES (5, '20835', 0, 0, 0, 0, '远方限功率运行状态', 'var_23136', 'B', 'notdefined', 'var_23136');
INSERT INTO `turbine_model_points` VALUES (6, '20835', 0, 0, 0, 0, '限电停机标志', 'var_23137', 'B', 'notdefined', 'var_23137');
INSERT INTO `turbine_model_points` VALUES (7, '20835', 0, 0, 0, 0, '本地有功控制使能状态', 'var_23138', 'B', 'notdefined', 'var_23138');
INSERT INTO `turbine_model_points` VALUES (8, '20835', 0, 0, 0, 0, '无功可调状态', 'var_23139', 'B', 'notdefined', 'var_23139');
INSERT INTO `turbine_model_points` VALUES (9, '20835', 0, 0, 0, 0, '远程启动', 'var_23140', 'B', 'notdefined', 'var_23140');
INSERT INTO `turbine_model_points` VALUES (10, '20835', 0, 0, 0, 0, '远程停机(限电停机)', 'var_23141', 'B', 'notdefined', 'var_23141');
INSERT INTO `turbine_model_points` VALUES (11, '20835', 0, 0, 0, 0, '远程复位', 'var_23142', 'B', 'notdefined', 'var_23142');
INSERT INTO `turbine_model_points` VALUES (12, '20835', 0, 0, 0, 0, 'C3柜高压负荷分位', 'var_28000', 'B', 'notdefined', 'var_28000');
INSERT INTO `turbine_model_points` VALUES (13, '20835', 0, 0, 0, 0, 'C3柜高压负荷合位', 'var_28001', 'B', 'notdefined', 'var_28001');
INSERT INTO `turbine_model_points` VALUES (14, '20835', 0, 0, 0, 0, '塔基SF6导流系统过载警告', 'var_38000', 'B', 'notdefined', 'var_38000');
INSERT INTO `turbine_model_points` VALUES (15, '20835', 0, 0, 0, 0, '塔基盐雾过滤过载警告', 'var_38001', 'B', 'notdefined', 'var_38001');
INSERT INTO `turbine_model_points` VALUES (16, '20835', 0, 0, 0, 0, '塔基盐雾过滤堵塞警告', 'var_38002', 'B', 'notdefined', 'var_38002');
INSERT INTO `turbine_model_points` VALUES (17, '20835', 0, 0, 0, 0, '塔基盐雾过滤故障警告', 'var_38003', 'B', 'notdefined', 'var_38003');
INSERT INTO `turbine_model_points` VALUES (18, '20835', 0, 0, 0, 0, '塔基SOS故障', 'var_38004', 'B', 'notdefined', 'var_38004');
INSERT INTO `turbine_model_points` VALUES (19, '20835', 0, 0, 0, 0, '后备电源过载故障', 'var_38005', 'B', 'notdefined', 'var_38005');
INSERT INTO `turbine_model_points` VALUES (20, '20835', 0, 0, 0, 0, '变桨系统闭环停机退出故障', 'var_38006', 'B', 'notdefined', 'var_38006');
INSERT INTO `turbine_model_points` VALUES (21, '20835', 0, 0, 0, 0, '变桨系统1#叶片进入闭环停机故障', 'var_38007', 'B', 'notdefined', 'var_38007');
INSERT INTO `turbine_model_points` VALUES (22, '20835', 0, 0, 0, 0, '变桨系统2#叶片进入闭环停机故障', 'var_38008', 'B', 'notdefined', 'var_38008');
INSERT INTO `turbine_model_points` VALUES (23, '20835', 0, 0, 0, 0, '变桨系统3#叶片进入闭环停机故障', 'var_38009', 'B', 'notdefined', 'var_38009');
INSERT INTO `turbine_model_points` VALUES (24, '20835', 0, 0, 0, 0, '发电机冷却液泄漏故障', 'var_38010', 'B', 'notdefined', 'var_38010');
INSERT INTO `turbine_model_points` VALUES (25, '20835', 0, 0, 0, 0, 'IPC风轮方位角标定未完成警告', 'var_38011', 'B', 'notdefined', 'var_38011');
INSERT INTO `turbine_model_points` VALUES (26, '20835', 0, 0, 0, 0, '变桨系统2#叶片直流母线电压', 'var_18026', 'F', 'notdefined', 'var_18026');
INSERT INTO `turbine_model_points` VALUES (27, '20835', 0, 0, 0, 0, '变桨系统1#叶片直流母线电压', 'var_18025', 'F', 'notdefined', 'var_18025');
INSERT INTO `turbine_model_points` VALUES (28, '20835', 0, 0, 0, 0, '主控核心控制器PitckKick桨距角叠加值', 'var_18024', 'F', 'notdefined', 'var_18024');
INSERT INTO `turbine_model_points` VALUES (29, '20835', 0, 0, 0, 0, '主控核心控制器PicthKick转矩叠加值', 'var_18023', 'F', 'notdefined', 'var_18023');
INSERT INTO `turbine_model_points` VALUES (30, '20835', 1, 0, 0, 0, '主控核心控制器PicthKick限制值', 'var_18022', 'F', 'notdefined', 'var_18022');
INSERT INTO `turbine_model_points` VALUES (31, '20835', 0, 0, 0, 0, '主控核心控制器PicthKick特征值', 'var_18021', 'F', 'notdefined', 'var_18021');
INSERT INTO `turbine_model_points` VALUES (32, '20835', 0, 0, 0, 0, '主控核心控制器变桨参考位置输出', 'var_18020', 'F', 'notdefined', 'var_18020');
INSERT INTO `turbine_model_points` VALUES (33, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长12', 'var_18019', 'F', 'notdefined', 'var_18019');
INSERT INTO `turbine_model_points` VALUES (34, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长11', 'var_18018', 'F', 'notdefined', 'var_18018');
INSERT INTO `turbine_model_points` VALUES (35, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长10', 'var_18017', 'F', 'notdefined', 'var_18017');
INSERT INTO `turbine_model_points` VALUES (36, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长9', 'var_18016', 'F', 'notdefined', 'var_18016');
INSERT INTO `turbine_model_points` VALUES (37, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长8', 'var_18015', 'F', 'notdefined', 'var_18015');
INSERT INTO `turbine_model_points` VALUES (38, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长7', 'var_18014', 'F', 'notdefined', 'var_18014');
INSERT INTO `turbine_model_points` VALUES (39, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长6', 'var_18013', 'F', 'notdefined', 'var_18013');
INSERT INTO `turbine_model_points` VALUES (40, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长5', 'var_18012', 'F', 'notdefined', 'var_18012');
INSERT INTO `turbine_model_points` VALUES (41, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长4', 'var_18011', 'F', 'notdefined', 'var_18011');
INSERT INTO `turbine_model_points` VALUES (42, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长3', 'var_18010', 'F', 'notdefined', 'var_18010');
INSERT INTO `turbine_model_points` VALUES (43, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长2', 'var_18009', 'F', 'notdefined', 'var_18009');
INSERT INTO `turbine_model_points` VALUES (44, '20835', 0, 0, 0, 0, '叶根载荷监测系统波长1', 'var_18008', 'F', 'notdefined', 'var_18008');
INSERT INTO `turbine_model_points` VALUES (45, '20835', 0, 0, 0, 0, '叶根载荷监测风轮不平衡弯矩', 'var_18007', 'F', 'notdefined', 'var_18007');
INSERT INTO `turbine_model_points` VALUES (46, '20835', 1, 0, 0, 0, '叶根载荷监测风轮方位角', 'var_18006', 'F', 'notdefined', 'var_18006');
INSERT INTO `turbine_model_points` VALUES (47, '20835', 1, 1, 0, 0, '叶根载荷监测叶片3挥舞弯矩', 'var_18005', 'F', 'notdefined', 'var_18005');
INSERT INTO `turbine_model_points` VALUES (48, '20835', 1, 1, 0, 0, '叶根载荷监测叶片2挥舞弯矩', 'var_18004', 'F', 'notdefined', 'var_18004');
INSERT INTO `turbine_model_points` VALUES (49, '20835', 1, 1, 0, 0, '叶根载荷监测叶片1挥舞弯矩', 'var_18003', 'F', 'notdefined', 'var_18003');
INSERT INTO `turbine_model_points` VALUES (50, '20835', 1, 1, 0, 0, '叶根载荷监测叶片3摆振弯矩', 'var_18002', 'F', 'notdefined', 'var_18002');
INSERT INTO `turbine_model_points` VALUES (51, '20835', 1, 1, 0, 0, '叶根载荷监测叶片2摆振弯矩', 'var_18001', 'F', 'notdefined', 'var_18001');
INSERT INTO `turbine_model_points` VALUES (52, '20835', 1, 1, 0, 0, '叶根载荷监测叶片1摆振弯矩', 'var_18000', 'F', 'notdefined', 'var_18000');
INSERT INTO `turbine_model_points` VALUES (53, '20835', 0, 0, 0, 0, '工作模式源码', 'workModeSrc', 'I', 'notdefined', 'workModeSrc');
INSERT INTO `turbine_model_points` VALUES (54, '20835', 1, 0, 1, 0, '故障', 'totalFaultBool', 'B', 'notdefined', 'totalFaultBool');
INSERT INTO `turbine_model_points` VALUES (55, '20835', 0, 0, 0, 0, '安全链断开', 'var_28', 'B', 'notdefined', 'var_28');
INSERT INTO `turbine_model_points` VALUES (56, '20835', 0, 0, 0, 0, '正常停机', 'var_29', 'B', 'notdefined', 'var_29');
INSERT INTO `turbine_model_points` VALUES (57, '20835', 0, 0, 0, 0, '快速停机', 'var_30', 'B', 'notdefined', 'var_30');
INSERT INTO `turbine_model_points` VALUES (58, '20835', 0, 0, 0, 0, '紧急停机', 'var_31', 'B', 'notdefined', 'var_31');
INSERT INTO `turbine_model_points` VALUES (59, '20835', 0, 0, 0, 0, '人工停机', 'var_32', 'B', 'notdefined', 'var_32');
INSERT INTO `turbine_model_points` VALUES (60, '20835', 0, 0, 0, 0, '人工开机', 'var_33', 'B', 'notdefined', 'var_33');
INSERT INTO `turbine_model_points` VALUES (61, '20835', 0, 0, 0, 0, '环境温度过低', 'var_37', 'B', 'notdefined', 'var_37');
INSERT INTO `turbine_model_points` VALUES (62, '20835', 0, 0, 0, 0, '无功设定状态', 'var_38', 'I', 'notdefined', 'var_38');
INSERT INTO `turbine_model_points` VALUES (63, '20835', 0, 0, 0, 0, '远程启动', 'var_45', 'B', 'notdefined', 'var_45');
INSERT INTO `turbine_model_points` VALUES (64, '20835', 0, 0, 0, 0, '远程停机', 'var_46', 'B', 'notdefined', 'var_46');
INSERT INTO `turbine_model_points` VALUES (65, '20835', 0, 0, 0, 0, '远程复位', 'var_47', 'B', 'notdefined', 'var_47');
INSERT INTO `turbine_model_points` VALUES (66, '20835', 0, 0, 0, 0, 'LVRT功能使能开启', 'var_64', 'B', 'notdefined', 'var_64');
INSERT INTO `turbine_model_points` VALUES (67, '20835', 0, 0, 0, 0, 'LVRT功能使能关闭', 'var_65', 'B', 'notdefined', 'var_65');
INSERT INTO `turbine_model_points` VALUES (68, '20835', 0, 0, 0, 0, 'LVRT功能使能状态反馈值', 'var_66', 'B', 'notdefined', 'var_66');
INSERT INTO `turbine_model_points` VALUES (69, '20835', 0, 0, 0, 0, '远方就地控制开关', 'var_67', 'B', 'notdefined', 'var_67');
INSERT INTO `turbine_model_points` VALUES (70, '20835', 0, 0, 0, 0, '本地状态时间', 'hourLocalState', 'I', 'h', 'hourLocalState');
INSERT INTO `turbine_model_points` VALUES (71, '20835', 1, 0, 0, 0, '3#叶片变桨速度', 'var_109', 'F', '°/s', 'var_109');
INSERT INTO `turbine_model_points` VALUES (72, '20835', 1, 0, 0, 0, '1#叶片变桨速度', 'var_107', 'F', '°/s', 'var_107');
INSERT INTO `turbine_model_points` VALUES (73, '20835', 0, 0, 0, 0, '转子刹车释放', 'var_137', 'B', 'notdefined', 'var_137');
INSERT INTO `turbine_model_points` VALUES (74, '20835', 0, 0, 0, 0, '齿轮箱润滑泵高速', 'var_140', 'B', 'notdefined', 'var_140');
INSERT INTO `turbine_model_points` VALUES (75, '20835', 0, 0, 0, 0, '齿轮箱润滑泵低速', 'var_141', 'B', 'notdefined', 'var_141');
INSERT INTO `turbine_model_points` VALUES (76, '20835', 0, 0, 0, 0, '齿轮箱离线过滤泵', 'var_144', 'B', 'notdefined', 'var_144');
INSERT INTO `turbine_model_points` VALUES (77, '20835', 0, 0, 0, 0, '信息类别', 'informationType', 'I', 'notdefined', 'informationType');
INSERT INTO `turbine_model_points` VALUES (78, '20835', 1, 1, 0, 0, '发电机冷却水泵', 'var_191', 'B', 'notdefined', 'var_191');
INSERT INTO `turbine_model_points` VALUES (79, '20835', 1, 1, 0, 0, '发电机冷却风扇1', 'var_192', 'B', 'notdefined', 'var_192');
INSERT INTO `turbine_model_points` VALUES (80, '20835', 0, 0, 0, 0, '发电机润滑泵', 'var_200', 'B', 'notdefined', 'var_200');
INSERT INTO `turbine_model_points` VALUES (81, '20835', 0, 0, 0, 0, '发电机加热器', 'var_201', 'B', 'notdefined', 'var_201');
INSERT INTO `turbine_model_points` VALUES (82, '20835', 0, 0, 0, 0, 'LVRT事件激活', 'var_230', 'B', 'notdefined', 'var_230');
INSERT INTO `turbine_model_points` VALUES (83, '20835', 1, 0, 1, 0, '并网', 'onGrid', 'B', 'notdefined', 'onGrid');
INSERT INTO `turbine_model_points` VALUES (84, '20835', 0, 0, 0, 0, '转子刹车超时故障', 'var_315', 'B', 'notdefined', 'var_315');
INSERT INTO `turbine_model_points` VALUES (85, '20835', 0, 0, 0, 0, '风暴', 'var_347', 'B', 'notdefined', 'var_347');
INSERT INTO `turbine_model_points` VALUES (86, '20835', 0, 0, 0, 0, '月发电量', 'var_177', 'F', 'kWh', 'var_177');
INSERT INTO `turbine_model_points` VALUES (87, '20835', 1, 0, 1, 0, '发电机转矩', 'var_226', 'F', 'Nm', 'var_226');
INSERT INTO `turbine_model_points` VALUES (88, '20835', 0, 0, 0, 0, '机舱指北方向', 'winDir', 'F', '°', 'winDir');
INSERT INTO `turbine_model_points` VALUES (89, '20835', 0, 0, 0, 0, '60s平均风速', 'var_358', 'F', 'm/s', 'var_358');
INSERT INTO `turbine_model_points` VALUES (90, '20835', 0, 0, 0, 0, '远程手动停机消息', 'var_377', 'B', 'notdefined', 'var_377');
INSERT INTO `turbine_model_points` VALUES (91, '20835', 0, 0, 0, 0, '偏航在顺时针运行模式', 'rightYawSingle', 'B', 'notdefined', 'rightYawSingle');
INSERT INTO `turbine_model_points` VALUES (92, '20835', 0, 0, 0, 0, '偏航在逆时针运行模式', 'leftYawSingle', 'B', 'notdefined', 'leftYawSingle');
INSERT INTO `turbine_model_points` VALUES (93, '20835', 0, 0, 0, 0, '偏航电机刹车', 'var_395', 'B', 'notdefined', 'var_395');
INSERT INTO `turbine_model_points` VALUES (94, '20835', 0, 0, 0, 0, '偏航刹车全部释放', 'var_396', 'B', 'notdefined', 'var_396');
INSERT INTO `turbine_model_points` VALUES (95, '20835', 0, 0, 0, 0, '偏航刹车部分释放', 'var_397', 'B', 'notdefined', 'var_397');
INSERT INTO `turbine_model_points` VALUES (96, '20835', 0, 0, 0, 0, '逆时针解缆激活', 'var_403', 'B', 'notdefined', 'var_403');
INSERT INTO `turbine_model_points` VALUES (97, '20835', 0, 0, 0, 0, '顺时针解缆激活', 'var_404', 'B', 'notdefined', 'var_404');
INSERT INTO `turbine_model_points` VALUES (98, '20835', 0, 0, 0, 0, 'PLC时间-时', 'var_426', 'I', 'h', 'var_426');
INSERT INTO `turbine_model_points` VALUES (99, '20835', 0, 0, 0, 0, 'PLC时间-分', 'var_427', 'I', 'm', 'var_427');
INSERT INTO `turbine_model_points` VALUES (100, '20835', 0, 0, 0, 0, 'PLC时间-秒', 'var_428', 'I', 's', 'var_428');
INSERT INTO `turbine_model_points` VALUES (101, '20835', 0, 0, 0, 0, 'PLC时间-年', 'var_429', 'I', 'y', 'var_429');
INSERT INTO `turbine_model_points` VALUES (102, '20835', 0, 0, 0, 0, 'PLC时间-月', 'var_430', 'I', 'M', 'var_430');
INSERT INTO `turbine_model_points` VALUES (103, '20835', 0, 0, 0, 0, 'PLC时间-日', 'var_431', 'I', 'd', 'var_431');
INSERT INTO `turbine_model_points` VALUES (104, '20835', 0, 0, 0, 0, '变流器故障', 'var_468', 'B', 'notdefined', 'var_468');
INSERT INTO `turbine_model_points` VALUES (105, '20835', 0, 0, 0, 0, '发电机超速故障', 'var_530', 'B', 'notdefined', 'var_530');
INSERT INTO `turbine_model_points` VALUES (106, '20835', 0, 0, 0, 0, '发电机绕组U1超温故障', 'var_572', 'B', 'notdefined', 'var_572');
INSERT INTO `turbine_model_points` VALUES (107, '20835', 0, 0, 0, 0, '发电机绕组U2超温故障', 'var_573', 'B', 'notdefined', 'var_573');
INSERT INTO `turbine_model_points` VALUES (108, '20835', 0, 0, 0, 0, '发电机绕组V1超温故障', 'var_574', 'B', 'notdefined', 'var_574');
INSERT INTO `turbine_model_points` VALUES (109, '20835', 0, 0, 0, 0, '发电机绕组V2超温故障', 'var_575', 'B', 'notdefined', 'var_575');
INSERT INTO `turbine_model_points` VALUES (110, '20835', 0, 0, 0, 0, '发电机绕组W1超温故障', 'var_576', 'B', 'notdefined', 'var_576');
INSERT INTO `turbine_model_points` VALUES (111, '20835', 0, 0, 0, 0, '发电机绕组W2超温故障', 'var_577', 'B', 'notdefined', 'var_577');
INSERT INTO `turbine_model_points` VALUES (112, '20835', 0, 0, 0, 0, '风暴停机状态', 'var_692', 'B', 'notdefined', 'var_692');
INSERT INTO `turbine_model_points` VALUES (113, '20835', 0, 0, 0, 0, '风机自身故障停机', 'faultOwnSingle', 'B', 'notdefined', 'faultOwnSingle');
INSERT INTO `turbine_model_points` VALUES (114, '20835', 0, 0, 0, 0, '故障停机', 'faultSingle', 'B', 'notdefined', 'faultSingle');
INSERT INTO `turbine_model_points` VALUES (115, '20835', 0, 0, 0, 0, '机组自身限功率运行状态', 'var_998', 'B', 'notdefined', 'var_998');
INSERT INTO `turbine_model_points` VALUES (116, '20835', 0, 0, 0, 0, '就地限功率运行状态', 'var_1001', 'B', 'notdefined', 'var_1001');
INSERT INTO `turbine_model_points` VALUES (117, '20835', 0, 0, 0, 0, '远方限功率运行状态', 'var_1002', 'B', 'notdefined', 'var_1002');
INSERT INTO `turbine_model_points` VALUES (118, '20835', 0, 0, 0, 0, '消息代码1', 'msgCode1', 'I', 'notdefined', 'msgCode1');
INSERT INTO `turbine_model_points` VALUES (119, '20835', 0, 0, 0, 0, '消息代码2', 'msgCode2', 'I', 'notdefined', 'msgCode2');
INSERT INTO `turbine_model_points` VALUES (120, '20835', 0, 0, 0, 0, '消息代码3', 'msgCode3', 'I', 'notdefined', 'msgCode3');
INSERT INTO `turbine_model_points` VALUES (121, '20835', 0, 0, 0, 0, '消息代码4', 'msgCode4', 'I', 'notdefined', 'msgCode4');
INSERT INTO `turbine_model_points` VALUES (122, '20835', 0, 0, 0, 0, '消息代码5', 'msgCode5', 'I', 'notdefined', 'msgCode5');
INSERT INTO `turbine_model_points` VALUES (123, '20835', 0, 0, 0, 0, '消息代码6', 'msgCode6', 'I', 'notdefined', 'msgCode6');
INSERT INTO `turbine_model_points` VALUES (124, '20835', 0, 0, 0, 0, '消息代码7', 'msgCode7', 'I', 'notdefined', 'msgCode7');
INSERT INTO `turbine_model_points` VALUES (125, '20835', 0, 0, 0, 0, '消息代码8', 'msgCode8', 'I', 'notdefined', 'msgCode8');
INSERT INTO `turbine_model_points` VALUES (126, '20835', 0, 0, 0, 0, '消息代码9', 'msgCode9', 'I', 'notdefined', 'msgCode9');
INSERT INTO `turbine_model_points` VALUES (127, '20835', 0, 0, 0, 0, '消息代码10', 'msgCode10', 'I', 'notdefined', 'msgCode10');
INSERT INTO `turbine_model_points` VALUES (128, '20835', 0, 0, 0, 0, '本地有功控制使能状态', 'var_1108', 'B', 'notdefined', 'var_1108');
INSERT INTO `turbine_model_points` VALUES (129, '20835', 0, 0, 0, 0, '风况超出运行范围', 'var_1150', 'B', 'notdefined', 'var_1150');
INSERT INTO `turbine_model_points` VALUES (130, '20835', 0, 0, 0, 0, '发电机DE端轴承超温故障', 'var_1228', 'B', 'notdefined', 'var_1228');
INSERT INTO `turbine_model_points` VALUES (131, '20835', 0, 0, 0, 0, '不可抗力时间', 'iafm', 'F', 'h', 'iafm');
INSERT INTO `turbine_model_points` VALUES (132, '20835', 0, 0, 0, 0, '暂停作业时间', 'ianos', 'F', 'h', 'ianos');
INSERT INTO `turbine_model_points` VALUES (133, '20835', 0, 0, 0, 0, '强制停机时间', 'ianofo', 'F', 'h', 'ianofo');
INSERT INTO `turbine_model_points` VALUES (134, '20835', 0, 0, 0, 0, '计划性改进时间', 'ianopca', 'F', 'h', 'ianopca');
INSERT INTO `turbine_model_points` VALUES (135, '20835', 0, 0, 0, 0, '定期维护时间', 'ianosm', 'F', 'h', 'ianosm');
INSERT INTO `turbine_model_points` VALUES (136, '20835', 0, 0, 0, 0, '超出电气规范时间', 'iaongel', 'F', 'h', 'iaongel');
INSERT INTO `turbine_model_points` VALUES (137, '20835', 0, 0, 0, 0, '指令停机时间', 'iaongrs', 'F', 'h', 'iaongrs');
INSERT INTO `turbine_model_points` VALUES (138, '20835', 0, 0, 0, 0, '超出其他环境条件时间', 'iaongeno', 'F', 'h', 'iaongeno');
INSERT INTO `turbine_model_points` VALUES (139, '20835', 0, 0, 0, 0, '无风时间', 'iaongenc', 'F', 'h', 'iaongenc');
INSERT INTO `turbine_model_points` VALUES (140, '20835', 0, 0, 0, 0, '正常发电运行时间', 'var_1050', 'F', 'h', 'var_1050');
INSERT INTO `turbine_model_points` VALUES (141, '20835', 0, 0, 0, 0, '顺时针偏航运行时间', 'hourRightYaw', 'F', 'h', 'hourRightYaw');
INSERT INTO `turbine_model_points` VALUES (142, '20835', 0, 0, 0, 0, '逆时针偏航运行时间', 'hourLeftYaw', 'F', 'h', 'hourLeftYaw');
INSERT INTO `turbine_model_points` VALUES (143, '20835', 1, 0, 0, 0, '机舱内湿度', 'var_374', 'F', '%', 'var_374');
INSERT INTO `turbine_model_points` VALUES (144, '20835', 1, 1, 1, 0, '机舱Y方向振动', 'var_383', 'F', 'm/s^2', 'var_383');
INSERT INTO `turbine_model_points` VALUES (145, '20835', 0, 0, 0, 0, '发电机NDE轴承超温故障', 'var_1229', 'B', 'notdefined', 'var_1229');
INSERT INTO `turbine_model_points` VALUES (146, '20835', 0, 0, 0, 0, '发电机冷却水入口温度过高故障', 'var_1232', 'B', 'notdefined', 'var_1232');
INSERT INTO `turbine_model_points` VALUES (147, '20835', 0, 0, 0, 0, '发电机功率曲线超下限故障', 'var_1244', 'B', 'notdefined', 'var_1244');
INSERT INTO `turbine_model_points` VALUES (148, '20835', 0, 0, 0, 0, '发电机功率曲线超上限警告', 'var_1245', 'B', 'notdefined', 'var_1245');
INSERT INTO `turbine_model_points` VALUES (149, '20835', 0, 0, 0, 0, '发电机速度波动过大故障', 'var_1246', 'B', 'notdefined', 'var_1246');
INSERT INTO `turbine_model_points` VALUES (150, '20835', 0, 0, 0, 0, '发电机功率波动过大故障', 'var_1247', 'B', 'notdefined', 'var_1247');
INSERT INTO `turbine_model_points` VALUES (151, '20835', 0, 0, 0, 0, '发电机冷却水入口温度过低故障', 'var_1250', 'B', 'notdefined', 'var_1250');
INSERT INTO `turbine_model_points` VALUES (152, '20835', 0, 0, 0, 0, '发电机冷却水泵过载故障', 'var_1252', 'B', 'notdefined', 'var_1252');
INSERT INTO `turbine_model_points` VALUES (153, '20835', 0, 0, 0, 0, '发电机滑环冷却风扇过载故障', 'var_1256', 'B', 'notdefined', 'var_1256');
INSERT INTO `turbine_model_points` VALUES (154, '20835', 0, 0, 0, 0, 'UPS电池容量低故障', 'var_1297', 'B', 'notdefined', 'var_1297');
INSERT INTO `turbine_model_points` VALUES (155, '20835', 0, 0, 0, 0, 'UPS旁路故障', 'var_1298', 'B', 'notdefined', 'var_1298');
INSERT INTO `turbine_model_points` VALUES (156, '20835', 0, 0, 0, 0, '事件日志复位（WTC系统故障）', 'var_1303', 'B', 'notdefined', 'var_1303');
INSERT INTO `turbine_model_points` VALUES (157, '20835', 0, 0, 0, 0, '无效处理（WTC系统故障）', 'var_1304', 'B', 'notdefined', 'var_1304');
INSERT INTO `turbine_model_points` VALUES (158, '20835', 0, 0, 0, 0, '无效OP-bit（WTC系统故障）', 'var_1305', 'B', 'notdefined', 'var_1305');
INSERT INTO `turbine_model_points` VALUES (159, '20835', 0, 0, 0, 0, '安装错误（WTC系统故障）', 'var_1306', 'B', 'notdefined', 'var_1306');
INSERT INTO `turbine_model_points` VALUES (160, '20835', 0, 0, 0, 0, '事件日志写溢出（WTC系统故障）', 'var_1307', 'B', 'notdefined', 'var_1307');
INSERT INTO `turbine_model_points` VALUES (161, '20835', 0, 0, 0, 0, '写权限已给出（WTC系统故障）', 'var_1308', 'B', 'notdefined', 'var_1308');
INSERT INTO `turbine_model_points` VALUES (162, '20835', 0, 0, 0, 0, '未找到名称（WTC系统故障）', 'var_1309', 'B', 'notdefined', 'var_1309');
INSERT INTO `turbine_model_points` VALUES (163, '20835', 0, 0, 0, 0, '命令已使用（WTC系统故障）', 'var_1310', 'B', 'notdefined', 'var_1310');
INSERT INTO `turbine_model_points` VALUES (164, '20835', 0, 0, 0, 0, '无效参数WTC系统故障', 'var_1311', 'B', 'notdefined', 'var_1311');
INSERT INTO `turbine_model_points` VALUES (165, '20835', 0, 0, 0, 0, '定时器已使用但未启动（WTC系统故障）', 'var_1312', 'B', 'notdefined', 'var_1312');
INSERT INTO `turbine_model_points` VALUES (166, '20835', 0, 0, 0, 0, 'I/O配置故障（WTC系统故障）', 'var_1313', 'B', 'notdefined', 'var_1313');
INSERT INTO `turbine_model_points` VALUES (167, '20835', 0, 0, 0, 0, '未知数据类型（WTC系统故障）', 'var_1315', 'B', 'notdefined', 'var_1315');
INSERT INTO `turbine_model_points` VALUES (168, '20835', 0, 0, 0, 0, '得出未知空指针（WTC系统故障）', 'var_1316', 'B', 'notdefined', 'var_1316');
INSERT INTO `turbine_model_points` VALUES (169, '20835', 0, 0, 0, 0, '无效CDI索引（WTC系统故障）', 'var_1317', 'B', 'notdefined', 'var_1317');
INSERT INTO `turbine_model_points` VALUES (170, '20835', 0, 0, 0, 0, '事件日志混乱（WTC系统故障）', 'var_1318', 'B', 'notdefined', 'var_1318');
INSERT INTO `turbine_model_points` VALUES (171, '20835', 0, 0, 0, 0, '签名故障（WTC系统故障）', 'var_1319', 'B', 'notdefined', 'var_1319');
INSERT INTO `turbine_model_points` VALUES (172, '20835', 0, 0, 0, 0, 'Nv类型变化（WTC系统故障）', 'var_1320', 'B', 'notdefined', 'var_1320');
INSERT INTO `turbine_model_points` VALUES (173, '20835', 0, 0, 0, 0, 'XML文件故障（WTC系统故障）', 'var_1321', 'B', 'notdefined', 'var_1321');
INSERT INTO `turbine_model_points` VALUES (174, '20835', 0, 0, 0, 0, '字符串太长（WTC系统故障）', 'var_1322', 'B', 'notdefined', 'var_1322');
INSERT INTO `turbine_model_points` VALUES (175, '20835', 0, 0, 0, 0, '默认状态开关终止（WTC系统故障）', 'var_1323', 'B', 'notdefined', 'var_1323');
INSERT INTO `turbine_model_points` VALUES (176, '20835', 0, 0, 0, 0, '错误的数据类型（WTC系统故障）', 'var_1324', 'B', 'notdefined', 'var_1324');
INSERT INTO `turbine_model_points` VALUES (177, '20835', 0, 0, 0, 0, '系统启动错误', 'var_1325', 'B', 'notdefined', 'var_1325');
INSERT INTO `turbine_model_points` VALUES (178, '20835', 0, 0, 0, 0, '许可密钥无效（WTC系统故障）', 'var_1326', 'B', 'notdefined', 'var_1326');
INSERT INTO `turbine_model_points` VALUES (179, '20835', 0, 0, 0, 0, '应用周期超限（WTC系统故障）', 'var_1327', 'B', 'notdefined', 'var_1327');
INSERT INTO `turbine_model_points` VALUES (180, '20835', 0, 0, 0, 0, '不能创建Nv文件', 'var_1328', 'B', 'notdefined', 'var_1328');
INSERT INTO `turbine_model_points` VALUES (181, '20835', 0, 0, 0, 0, 'NV-RAM error（WTC系统错误）', 'var_1329', 'B', 'notdefined', 'var_1329');
INSERT INTO `turbine_model_points` VALUES (182, '20835', 0, 0, 0, 0, 'SEESF应用程序命令丢失（WTC系统错误）', 'var_1331', 'B', 'notdefined', 'var_1331');
INSERT INTO `turbine_model_points` VALUES (183, '20835', 0, 0, 0, 0, 'CanKK正在重启', 'var_1332', 'B', 'notdefined', 'var_1332');
INSERT INTO `turbine_model_points` VALUES (184, '20835', 0, 0, 0, 0, '错误风机类型（WTC系统错误）', 'var_1333', 'B', 'notdefined', 'var_1333');
INSERT INTO `turbine_model_points` VALUES (185, '20835', 0, 0, 0, 0, '操作系统相关错误（WTC系统错误）', 'var_1334', 'B', 'notdefined', 'var_1334');
INSERT INTO `turbine_model_points` VALUES (186, '20835', 0, 0, 0, 0, '无效的紧急停机回路选择故障', 'var_1337', 'B', 'notdefined', 'var_1337');
INSERT INTO `turbine_model_points` VALUES (187, '20835', 0, 0, 0, 0, 'UPS系统配置无效故障', 'var_1351', 'B', 'notdefined', 'var_1351');
INSERT INTO `turbine_model_points` VALUES (188, '20835', 0, 0, 0, 0, '环境温度高故障', 'var_1354', 'B', 'notdefined', 'var_1354');
INSERT INTO `turbine_model_points` VALUES (189, '20835', 0, 0, 0, 0, '机舱振动10分钟平均值超限故障', 'var_1364', 'B', 'notdefined', 'var_1364');
INSERT INTO `turbine_model_points` VALUES (190, '20835', 0, 0, 0, 0, '转子刹车释放测试失败故障', 'var_1369', 'B', 'notdefined', 'var_1369');
INSERT INTO `turbine_model_points` VALUES (191, '20835', 0, 0, 0, 0, '转子超速故障', 'var_1370', 'B', 'notdefined', 'var_1370');
INSERT INTO `turbine_model_points` VALUES (192, '20835', 0, 0, 0, 0, '转子极端超速故障', 'var_1373', 'B', 'notdefined', 'var_1373');
INSERT INTO `turbine_model_points` VALUES (193, '20835', 0, 0, 0, 0, '发电机极端超速故障', 'var_1374', 'B', 'notdefined', 'var_1374');
INSERT INTO `turbine_model_points` VALUES (194, '20835', 0, 0, 0, 0, '安全控制器激活故障', 'var_1375', 'B', 'notdefined', 'var_1375');
INSERT INTO `turbine_model_points` VALUES (195, '20835', 0, 0, 0, 0, '安全链故障', 'var_1382', 'B', 'notdefined', 'var_1382');
INSERT INTO `turbine_model_points` VALUES (196, '20835', 0, 0, 0, 0, '安全控制器无效厂家故障', 'var_1384', 'B', 'notdefined', 'var_1384');
INSERT INTO `turbine_model_points` VALUES (197, '20835', 0, 0, 0, 0, '安全控制器版本读出故障', 'var_1385', 'B', 'notdefined', 'var_1385');
INSERT INTO `turbine_model_points` VALUES (198, '20835', 0, 0, 0, 0, '安全链测试失败', 'var_1390', 'B', 'notdefined', 'var_1390');
INSERT INTO `turbine_model_points` VALUES (199, '20835', 0, 0, 0, 0, '停机空转刹车未投入', 'var_1393', 'B', 'notdefined', 'var_1393');
INSERT INTO `turbine_model_points` VALUES (200, '20835', 0, 0, 0, 0, '箱变温度保护激活故障', 'var_1396', 'B', 'notdefined', 'var_1396');
INSERT INTO `turbine_model_points` VALUES (201, '20835', 0, 0, 0, 0, '偏航速度过低故障', 'var_1408', 'B', 'notdefined', 'var_1408');
INSERT INTO `turbine_model_points` VALUES (202, '20835', 0, 0, 0, 0, '偏航极限开关触发', 'var_1409', 'B', 'notdefined', 'var_1409');
INSERT INTO `turbine_model_points` VALUES (203, '20835', 0, 0, 0, 0, '变桨系统测试失败故障', 'var_1487', 'B', 'notdefined', 'var_1487');
INSERT INTO `turbine_model_points` VALUES (204, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片编码器故障', 'var_1500', 'B', 'notdefined', 'var_1500');
INSERT INTO `turbine_model_points` VALUES (205, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片编码器故障', 'var_1501', 'B', 'notdefined', 'var_1501');
INSERT INTO `turbine_model_points` VALUES (206, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片编码器故障', 'var_1502', 'B', 'notdefined', 'var_1502');
INSERT INTO `turbine_model_points` VALUES (207, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片电机温度过高故障', 'var_1510', 'B', 'notdefined', 'var_1510');
INSERT INTO `turbine_model_points` VALUES (208, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片电机温度过高故障', 'var_1512', 'B', 'notdefined', 'var_1512');
INSERT INTO `turbine_model_points` VALUES (209, '20835', 0, 0, 0, 0, '速度传感器故障', 'var_1582', 'B', 'notdefined', 'var_1582');
INSERT INTO `turbine_model_points` VALUES (210, '20835', 0, 0, 0, 0, '发电机DE端轴承温度警告', 'var_1593', 'B', 'notdefined', 'var_1593');
INSERT INTO `turbine_model_points` VALUES (211, '20835', 1, 0, 0, 0, '最新故障代码', 'faultCode', 'I', 'notdefined', 'faultCode');
INSERT INTO `turbine_model_points` VALUES (212, '20835', 1, 1, 0, 0, '塔基柜冷却风扇', 'var_1684', 'B', 'notdefined', 'var_1684');
INSERT INTO `turbine_model_points` VALUES (213, '20835', 0, 0, 0, 0, '环网柜控制电源消失报警', 'var_1701', 'B', 'notdefined', 'var_1701');
INSERT INTO `turbine_model_points` VALUES (214, '20835', 0, 0, 0, 0, '环网柜SF6气压报警', 'var_1702', 'B', 'notdefined', 'var_1702');
INSERT INTO `turbine_model_points` VALUES (215, '20835', 0, 0, 0, 0, '顺时针偏航次数', 'var_1744', 'I', 'notdefined', 'var_1744');
INSERT INTO `turbine_model_points` VALUES (216, '20835', 0, 0, 0, 0, '逆时针偏航次数', 'var_1745', 'I', 'notdefined', 'var_1745');
INSERT INTO `turbine_model_points` VALUES (217, '20835', 0, 0, 0, 0, '远程维护', 'var_1754', 'B', 'notdefined', 'var_1754');
INSERT INTO `turbine_model_points` VALUES (218, '20835', 0, 0, 0, 0, '消防控制', 'var_1755', 'B', 'notdefined', 'var_1755');
INSERT INTO `turbine_model_points` VALUES (219, '20835', 0, 0, 0, 0, '齿轮箱润滑泵2高速', 'var_1756', 'B', 'notdefined', 'var_1756');
INSERT INTO `turbine_model_points` VALUES (220, '20835', 0, 0, 0, 0, '齿轮箱润滑泵2低速', 'var_1757', 'B', 'notdefined', 'var_1757');
INSERT INTO `turbine_model_points` VALUES (221, '20835', 0, 0, 0, 0, '变流器加热请求状态', 'var_1758', 'B', 'notdefined', 'var_1758');
INSERT INTO `turbine_model_points` VALUES (222, '20835', 0, 0, 0, 0, '齿轮箱油位信号', 'var_1759', 'B', 'notdefined', 'var_1759');
INSERT INTO `turbine_model_points` VALUES (223, '20835', 0, 0, 0, 0, '机舱空-空冷', 'var_1760', 'B', 'notdefined', 'var_1760');
INSERT INTO `turbine_model_points` VALUES (224, '20835', 0, 0, 0, 0, '消防系统运行状态反馈', 'var_1771', 'B', 'notdefined', 'var_1771');
INSERT INTO `turbine_model_points` VALUES (225, '20835', 0, 0, 0, 0, '轮毂烟感警告', 'var_1782', 'B', 'notdefined', 'var_1782');
INSERT INTO `turbine_model_points` VALUES (226, '20835', 0, 0, 0, 0, '警告代码1', 'alarmCode1', 'I', 'notdefined', 'alarmCode1');
INSERT INTO `turbine_model_points` VALUES (227, '20835', 0, 0, 0, 0, '警告代码2', 'alarmCode2', 'I', 'notdefined', 'alarmCode2');
INSERT INTO `turbine_model_points` VALUES (228, '20835', 0, 0, 0, 0, '电网A相电压2', 'var_1762', 'F', 'V', 'var_1762');
INSERT INTO `turbine_model_points` VALUES (229, '20835', 0, 0, 0, 0, '电网A相电流2', 'var_1761', 'F', 'A', 'var_1761');
INSERT INTO `turbine_model_points` VALUES (230, '20835', 0, 0, 0, 0, '环网柜继电保护动作', 'var_1709', 'B', 'notdefined', 'var_1709');
INSERT INTO `turbine_model_points` VALUES (231, '20835', 0, 0, 0, 0, '机舱前端温度', 'var_1644', 'F', '°C', 'var_1644');
INSERT INTO `turbine_model_points` VALUES (232, '20835', 0, 0, 0, 0, '600s平均风向差值', 'var_1643', 'F', '°', 'var_1643');
INSERT INTO `turbine_model_points` VALUES (233, '20835', 0, 0, 0, 0, '变压器超温报警', 'var_1705', 'B', 'notdefined', 'var_1705');
INSERT INTO `turbine_model_points` VALUES (234, '20835', 0, 0, 0, 0, '变压器超温跳闸', 'var_1706', 'B', 'notdefined', 'var_1706');
INSERT INTO `turbine_model_points` VALUES (235, '20835', 0, 0, 0, 0, '变压器工作电源消失报警', 'var_1703', 'B', 'notdefined', 'var_1703');
INSERT INTO `turbine_model_points` VALUES (236, '20835', 0, 0, 0, 0, '变压器温控器故障', 'var_1704', 'B', 'notdefined', 'var_1704');
INSERT INTO `turbine_model_points` VALUES (237, '20835', 0, 0, 0, 0, '功率因数', 'var_1564', 'F', 'notdefined', 'var_1564');
INSERT INTO `turbine_model_points` VALUES (238, '20835', 0, 0, 0, 0, '最小变桨角度', 'var_1686', 'F', '°', 'var_1686');
INSERT INTO `turbine_model_points` VALUES (239, '20835', 0, 0, 0, 0, '上网日发电量', 'var_1688', 'F', 'kWh', 'var_1688');
INSERT INTO `turbine_model_points` VALUES (240, '20835', 0, 0, 0, 0, '上网总电量', 'var_1687', 'F', 'kWh', 'var_1687');
INSERT INTO `turbine_model_points` VALUES (241, '20835', 0, 0, 0, 0, '塔基控制柜温度2', 'var_1769', 'F', '°C', 'var_1769');
INSERT INTO `turbine_model_points` VALUES (242, '20835', 0, 0, 0, 0, '机舱控制柜温度3', 'var_1768', 'F', '°C', 'var_1768');
INSERT INTO `turbine_model_points` VALUES (243, '20835', 0, 0, 0, 0, '机舱控制柜温度2', 'var_1767', 'F', '°C', 'var_1767');
INSERT INTO `turbine_model_points` VALUES (244, '20835', 0, 0, 0, 0, '电网C相电压2', 'var_1766', 'F', 'V', 'var_1766');
INSERT INTO `turbine_model_points` VALUES (245, '20835', 0, 0, 0, 0, '电网C相电流2', 'var_1765', 'F', 'A', 'var_1765');
INSERT INTO `turbine_model_points` VALUES (246, '20835', 0, 0, 0, 0, '电网B相电压2', 'var_1764', 'F', 'V', 'var_1764');
INSERT INTO `turbine_model_points` VALUES (247, '20835', 0, 0, 0, 0, '电网B相电流2', 'var_1763', 'F', 'A', 'var_1763');
INSERT INTO `turbine_model_points` VALUES (248, '20835', 0, 0, 0, 0, '警告代码3', 'alarmCode3', 'I', 'notdefined', 'alarmCode3');
INSERT INTO `turbine_model_points` VALUES (249, '20835', 0, 0, 0, 0, '警告代码4', 'alarmCode4', 'I', 'notdefined', 'alarmCode4');
INSERT INTO `turbine_model_points` VALUES (250, '20835', 0, 0, 0, 0, '警告代码5', 'alarmCode5', 'I', 'notdefined', 'alarmCode5');
INSERT INTO `turbine_model_points` VALUES (251, '20835', 0, 0, 0, 0, '警告代码6', 'alarmCode6', 'I', 'notdefined', 'alarmCode6');
INSERT INTO `turbine_model_points` VALUES (252, '20835', 0, 0, 0, 0, '警告代码7', 'alarmCode7', 'I', 'notdefined', 'alarmCode7');
INSERT INTO `turbine_model_points` VALUES (253, '20835', 0, 0, 0, 0, '警告代码8', 'alarmCode8', 'I', 'notdefined', 'alarmCode8');
INSERT INTO `turbine_model_points` VALUES (254, '20835', 0, 0, 0, 0, '警告代码9', 'alarmCode9', 'I', 'notdefined', 'alarmCode9');
INSERT INTO `turbine_model_points` VALUES (255, '20835', 0, 0, 0, 0, '警告代码10', 'alarmCode10', 'I', 'notdefined', 'alarmCode10');
INSERT INTO `turbine_model_points` VALUES (256, '20835', 0, 0, 0, 0, '小于额定限功率标记', 'lessRatedPowerBool', 'B', 'notdefined', 'lessRatedPowerBool');
INSERT INTO `turbine_model_points` VALUES (257, '20835', 0, 0, 0, 0, '链接列表故障（WTC系统故障）', 'var_1902', 'B', 'notdefined', 'var_1902');
INSERT INTO `turbine_model_points` VALUES (258, '20835', 0, 0, 0, 0, 'NV文件不存在警告（WTC系统警告）', 'var_1908', 'B', 'notdefined', 'var_1908');
INSERT INTO `turbine_model_points` VALUES (259, '20835', 0, 0, 0, 0, '事件禁止警告（WTC系统警告）', 'var_1914', 'B', 'notdefined', 'var_1914');
INSERT INTO `turbine_model_points` VALUES (260, '20835', 0, 0, 0, 0, '变量手动控制（WTC系统警告）', 'var_1916', 'B', 'notdefined', 'var_1916');
INSERT INTO `turbine_model_points` VALUES (261, '20835', 0, 0, 0, 0, 'NV-RAM和制造商不匹配（WTC系统故障）', 'var_1918', 'B', 'notdefined', 'var_1918');
INSERT INTO `turbine_model_points` VALUES (262, '20835', 0, 0, 0, 0, 'EtherCAT总线错误（WTC系统故障）', 'var_1921', 'B', 'notdefined', 'var_1921');
INSERT INTO `turbine_model_points` VALUES (263, '20835', 0, 0, 0, 0, 'Application watchdog引起重启（WTC系统错误）', 'var_1923', 'B', 'notdefined', 'var_1923');
INSERT INTO `turbine_model_points` VALUES (264, '20835', 0, 0, 0, 0, '虚拟模块存在（WTC系统警告）', 'var_1925', 'B', 'notdefined', 'var_1925');
INSERT INTO `turbine_model_points` VALUES (265, '20835', 0, 0, 0, 0, '远程维护模式使能（WTC系统警告）', 'var_1927', 'B', 'notdefined', 'var_1927');
INSERT INTO `turbine_model_points` VALUES (266, '20835', 0, 0, 0, 0, 'EtherCAT警告', 'var_1928', 'B', 'notdefined', 'var_1928');
INSERT INTO `turbine_model_points` VALUES (267, '20835', 0, 0, 0, 0, '不能备份变量NV文件警告', 'var_1930', 'B', 'notdefined', 'var_1930');
INSERT INTO `turbine_model_points` VALUES (268, '20835', 0, 0, 0, 0, '调试模式激活警告', 'var_1931', 'B', 'notdefined', 'var_1931');
INSERT INTO `turbine_model_points` VALUES (269, '20835', 0, 0, 0, 0, '预留系统故障46', 'var_1933', 'B', 'notdefined', 'var_1933');
INSERT INTO `turbine_model_points` VALUES (270, '20835', 0, 0, 0, 0, '预留系统故障47', 'var_1934', 'B', 'notdefined', 'var_1934');
INSERT INTO `turbine_model_points` VALUES (271, '20835', 0, 0, 0, 0, '预留系统故障48', 'var_1935', 'B', 'notdefined', 'var_1935');
INSERT INTO `turbine_model_points` VALUES (272, '20835', 0, 0, 0, 0, 'IO口相关警告（WTC系统警告）', 'var_1936', 'B', 'notdefined', 'var_1936');
INSERT INTO `turbine_model_points` VALUES (273, '20835', 0, 0, 0, 0, '齿轮箱高速侧轴承1温度过高', 'var_1937', 'B', 'notdefined', 'var_1937');
INSERT INTO `turbine_model_points` VALUES (274, '20835', 0, 0, 0, 0, '齿轮箱高速侧轴承1温度高警告', 'var_1938', 'B', 'notdefined', 'var_1938');
INSERT INTO `turbine_model_points` VALUES (275, '20835', 0, 0, 0, 0, '齿轮箱高速侧轴承2温度过高', 'var_1939', 'B', 'notdefined', 'var_1939');
INSERT INTO `turbine_model_points` VALUES (276, '20835', 0, 0, 0, 0, '齿轮箱高速侧轴承2温度高警告', 'var_1940', 'B', 'notdefined', 'var_1940');
INSERT INTO `turbine_model_points` VALUES (277, '20835', 0, 0, 0, 0, '齿轮箱油泵电机待机加热过载故障', 'var_1941', 'B', 'notdefined', 'var_1941');
INSERT INTO `turbine_model_points` VALUES (278, '20835', 0, 0, 0, 0, '齿轮箱油旁路过滤器压力开关警告', 'var_1942', 'B', 'notdefined', 'var_1942');
INSERT INTO `turbine_model_points` VALUES (279, '20835', 0, 0, 0, 0, '齿轮箱旁路过滤电机过载故障', 'var_1943', 'B', 'notdefined', 'var_1943');
INSERT INTO `turbine_model_points` VALUES (280, '20835', 0, 0, 0, 0, '齿轮箱油压差高警告', 'var_1944', 'B', 'notdefined', 'var_1944');
INSERT INTO `turbine_model_points` VALUES (281, '20835', 0, 0, 0, 0, '齿轮箱油压差高故障', 'var_1945', 'B', 'notdefined', 'var_1945');
INSERT INTO `turbine_model_points` VALUES (282, '20835', 0, 0, 0, 0, '齿轮箱怠速泵过滤器压差高警告', 'var_1946', 'B', 'notdefined', 'var_1946');
INSERT INTO `turbine_model_points` VALUES (283, '20835', 0, 0, 0, 0, '齿轮箱怠速泵过滤器压差高故障', 'var_1947', 'B', 'notdefined', 'var_1947');
INSERT INTO `turbine_model_points` VALUES (284, '20835', 0, 0, 0, 0, '齿轮箱油泵1过滤器压差高警告', 'var_1948', 'B', 'notdefined', 'var_1948');
INSERT INTO `turbine_model_points` VALUES (285, '20835', 0, 0, 0, 0, '齿轮箱油泵1过滤器压差高故障', 'var_1949', 'B', 'notdefined', 'var_1949');
INSERT INTO `turbine_model_points` VALUES (286, '20835', 0, 0, 0, 0, '齿轮箱油泵2过滤器压差高警告', 'var_1950', 'B', 'notdefined', 'var_1950');
INSERT INTO `turbine_model_points` VALUES (287, '20835', 0, 0, 0, 0, '齿轮箱油泵2过滤器压差高故障', 'var_1951', 'B', 'notdefined', 'var_1951');
INSERT INTO `turbine_model_points` VALUES (288, '20835', 0, 0, 0, 0, '齿轮箱入口压力高警告', 'var_1952', 'B', 'notdefined', 'var_1952');
INSERT INTO `turbine_model_points` VALUES (289, '20835', 0, 0, 0, 0, '齿轮箱入口压力低警告', 'var_1953', 'B', 'notdefined', 'var_1953');
INSERT INTO `turbine_model_points` VALUES (290, '20835', 0, 0, 0, 0, '齿轮箱入口压力太高故障', 'var_1954', 'B', 'notdefined', 'var_1954');
INSERT INTO `turbine_model_points` VALUES (291, '20835', 0, 0, 0, 0, '齿轮箱入口压力太低故障', 'var_1955', 'B', 'notdefined', 'var_1955');
INSERT INTO `turbine_model_points` VALUES (292, '20835', 0, 0, 0, 0, '齿轮箱油入口温度过高警告', 'var_1956', 'B', 'notdefined', 'var_1956');
INSERT INTO `turbine_model_points` VALUES (293, '20835', 0, 0, 0, 0, '高速轴刹车压力', 'var_1890', 'F', 'Bar', 'var_1890');
INSERT INTO `turbine_model_points` VALUES (294, '20835', 0, 0, 0, 0, '齿轮箱油入口温度过低警告', 'var_1957', 'B', 'notdefined', 'var_1957');
INSERT INTO `turbine_model_points` VALUES (295, '20835', 0, 0, 0, 0, '齿轮箱油入口温度过高故障', 'var_1958', 'B', 'notdefined', 'var_1958');
INSERT INTO `turbine_model_points` VALUES (296, '20835', 0, 0, 0, 0, '齿轮箱油入口温度过低故障', 'var_1959', 'B', 'notdefined', 'var_1959');
INSERT INTO `turbine_model_points` VALUES (297, '20835', 0, 0, 0, 0, '齿轮箱油液位太低故障', 'var_1960', 'B', 'notdefined', 'var_1960');
INSERT INTO `turbine_model_points` VALUES (298, '20835', 0, 0, 0, 0, '齿轮箱出口油压过高警告', 'var_1961', 'B', 'notdefined', 'var_1961');
INSERT INTO `turbine_model_points` VALUES (299, '20835', 0, 0, 0, 0, '齿轮箱出口油压过低警告', 'var_1962', 'B', 'notdefined', 'var_1962');
INSERT INTO `turbine_model_points` VALUES (300, '20835', 0, 0, 0, 0, '齿轮箱出口油压过高故障', 'var_1963', 'B', 'notdefined', 'var_1963');
INSERT INTO `turbine_model_points` VALUES (301, '20835', 0, 0, 0, 0, '齿轮箱出口油压过低故障', 'var_1964', 'B', 'notdefined', 'var_1964');
INSERT INTO `turbine_model_points` VALUES (302, '20835', 0, 0, 0, 0, '齿轮箱油泵电机1过载故障', 'var_1965', 'B', 'notdefined', 'var_1965');
INSERT INTO `turbine_model_points` VALUES (303, '20835', 0, 0, 0, 0, '齿轮箱油泵电机2过载故障', 'var_1966', 'B', 'notdefined', 'var_1966');
INSERT INTO `turbine_model_points` VALUES (304, '20835', 0, 0, 0, 0, '齿轮箱油池温度高警告', 'var_1967', 'B', 'notdefined', 'var_1967');
INSERT INTO `turbine_model_points` VALUES (305, '20835', 0, 0, 0, 0, '齿轮箱油池温度低警告', 'var_1968', 'B', 'notdefined', 'var_1968');
INSERT INTO `turbine_model_points` VALUES (306, '20835', 0, 0, 0, 0, '齿轮箱油池温度高故障', 'var_1969', 'B', 'notdefined', 'var_1969');
INSERT INTO `turbine_model_points` VALUES (307, '20835', 0, 0, 0, 0, '齿轮箱油池温度低故障', 'var_1970', 'B', 'notdefined', 'var_1970');
INSERT INTO `turbine_model_points` VALUES (308, '20835', 0, 0, 0, 0, '齿轮箱油旁路过滤器压差太高故障', 'var_1971', 'B', 'notdefined', 'var_1971');
INSERT INTO `turbine_model_points` VALUES (309, '20835', 0, 0, 0, 0, '偏航条件解缆激活', 'var_1973', 'B', 'notdefined', 'var_1973');
INSERT INTO `turbine_model_points` VALUES (310, '20835', 0, 0, 0, 0, '偏航无条件解缆激活', 'var_1974', 'B', 'notdefined', 'var_1974');
INSERT INTO `turbine_model_points` VALUES (311, '20835', 0, 0, 0, 0, '机舱偏航未移动故障', 'var_1975', 'B', 'notdefined', 'var_1975');
INSERT INTO `turbine_model_points` VALUES (312, '20835', 0, 0, 0, 0, '偏航风向失调超过最大故障', 'var_1976', 'B', 'notdefined', 'var_1976');
INSERT INTO `turbine_model_points` VALUES (313, '20835', 0, 0, 0, 0, '偏航电缆扭揽相关位置未校准警告', 'var_1978', 'B', 'notdefined', 'var_1978');
INSERT INTO `turbine_model_points` VALUES (314, '20835', 0, 0, 0, 0, '偏航位置未校准警告', 'var_1979', 'B', 'notdefined', 'var_1979');
INSERT INTO `turbine_model_points` VALUES (315, '20835', 0, 0, 0, 0, '偏航负载位置未校准警告', 'var_1980', 'B', 'notdefined', 'var_1980');
INSERT INTO `turbine_model_points` VALUES (316, '20835', 0, 0, 0, 0, '偏航系统参数配置无效故障', 'var_1981', 'B', 'notdefined', 'var_1981');
INSERT INTO `turbine_model_points` VALUES (317, '20835', 0, 0, 0, 0, '偏航风向600s平均值失调超过最大故障', 'var_1982', 'B', 'notdefined', 'var_1982');
INSERT INTO `turbine_model_points` VALUES (318, '20835', 0, 0, 0, 0, '偏航电机最大时间超限故障', 'var_1983', 'B', 'notdefined', 'var_1983');
INSERT INTO `turbine_model_points` VALUES (319, '20835', 0, 0, 0, 0, '偏航电机1过载故障', 'var_1984', 'B', 'notdefined', 'var_1984');
INSERT INTO `turbine_model_points` VALUES (320, '20835', 0, 0, 0, 0, '偏航电机2过载故障', 'var_1985', 'B', 'notdefined', 'var_1985');
INSERT INTO `turbine_model_points` VALUES (321, '20835', 0, 0, 0, 0, '偏航电机3过载故障', 'var_1986', 'B', 'notdefined', 'var_1986');
INSERT INTO `turbine_model_points` VALUES (322, '20835', 0, 0, 0, 0, '偏航电机4过载故障', 'var_1987', 'B', 'notdefined', 'var_1987');
INSERT INTO `turbine_model_points` VALUES (323, '20835', 0, 0, 0, 0, '偏航电机5过载故障', 'var_1988', 'B', 'notdefined', 'var_1988');
INSERT INTO `turbine_model_points` VALUES (324, '20835', 0, 0, 0, 0, '偏航电机6过载故障', 'var_1989', 'B', 'notdefined', 'var_1989');
INSERT INTO `turbine_model_points` VALUES (325, '20835', 0, 0, 0, 0, '偏航变频器故障', 'var_1990', 'B', 'notdefined', 'var_1990');
INSERT INTO `turbine_model_points` VALUES (326, '20835', 0, 0, 0, 0, '偏航电机电流高警告', 'var_1991', 'B', 'notdefined', 'var_1991');
INSERT INTO `turbine_model_points` VALUES (327, '20835', 0, 0, 0, 0, '偏航电机刹车过载故障', 'var_1992', 'B', 'notdefined', 'var_1992');
INSERT INTO `turbine_model_points` VALUES (328, '20835', 0, 0, 0, 0, '偏航在刹车时进行偏航移动故障', 'var_1993', 'B', 'notdefined', 'var_1993');
INSERT INTO `turbine_model_points` VALUES (329, '20835', 0, 0, 0, 0, '偏航变频器警告', 'var_1994', 'B', 'notdefined', 'var_1994');
INSERT INTO `turbine_model_points` VALUES (330, '20835', 0, 0, 0, 0, '偏航变频器内部超极限警告', 'var_1995', 'B', 'notdefined', 'var_1995');
INSERT INTO `turbine_model_points` VALUES (331, '20835', 0, 0, 0, 0, '偏航电机加热过载警告', 'var_1996', 'B', 'notdefined', 'var_1996');
INSERT INTO `turbine_model_points` VALUES (332, '20835', 0, 0, 0, 0, '偏航电机7过载故障', 'var_1997', 'B', 'notdefined', 'var_1997');
INSERT INTO `turbine_model_points` VALUES (333, '20835', 0, 0, 0, 0, '偏航电机8过载故障', 'var_1998', 'B', 'notdefined', 'var_1998');
INSERT INTO `turbine_model_points` VALUES (334, '20835', 0, 0, 0, 0, '偏航齿轮润滑油脂液位低警告', 'var_1999', 'B', 'notdefined', 'var_1999');
INSERT INTO `turbine_model_points` VALUES (335, '20835', 0, 0, 0, 0, '偏航轴承润滑油脂液位低警告', 'var_2001', 'B', 'notdefined', 'var_2001');
INSERT INTO `turbine_model_points` VALUES (336, '20835', 0, 0, 0, 0, '偏航齿轮润滑报警故障', 'var_2002', 'B', 'notdefined', 'var_2002');
INSERT INTO `turbine_model_points` VALUES (337, '20835', 0, 0, 0, 0, '偏航轴承润滑报警故障', 'var_2003', 'B', 'notdefined', 'var_2003');
INSERT INTO `turbine_model_points` VALUES (338, '20835', 0, 0, 0, 0, '偏航变频器通讯错误故障', 'var_2004', 'B', 'notdefined', 'var_2004');
INSERT INTO `turbine_model_points` VALUES (339, '20835', 0, 0, 0, 0, '超大风偏航策略激活故障', 'var_2005', 'B', 'notdefined', 'var_2005');
INSERT INTO `turbine_model_points` VALUES (340, '20835', 0, 0, 0, 0, '偏航轴承润滑剩余时间极限超限警告', 'var_2006', 'B', 'notdefined', 'var_2006');
INSERT INTO `turbine_model_points` VALUES (341, '20835', 0, 0, 0, 0, '偏航齿轮润滑剩余时间极限超限警告', 'var_2007', 'B', 'notdefined', 'var_2007');
INSERT INTO `turbine_model_points` VALUES (342, '20835', 0, 0, 0, 0, '偏航变频器转矩超限警告', 'var_2008', 'B', 'notdefined', 'var_2008');
INSERT INTO `turbine_model_points` VALUES (343, '20835', 0, 0, 0, 0, '主轴承前端温度高故障', 'var_2009', 'B', 'notdefined', 'var_2009');
INSERT INTO `turbine_model_points` VALUES (344, '20835', 0, 0, 0, 0, '主轴承后端温度高故障', 'var_2010', 'B', 'notdefined', 'var_2010');
INSERT INTO `turbine_model_points` VALUES (345, '20835', 0, 0, 0, 0, '主轴承前端温度高警告', 'var_2011', 'B', 'notdefined', 'var_2011');
INSERT INTO `turbine_model_points` VALUES (346, '20835', 0, 0, 0, 0, '主轴承后端温度高警告', 'var_2012', 'B', 'notdefined', 'var_2012');
INSERT INTO `turbine_model_points` VALUES (347, '20835', 0, 0, 0, 0, '主轴承温度1过高故障', 'var_2013', 'B', 'notdefined', 'var_2013');
INSERT INTO `turbine_model_points` VALUES (348, '20835', 0, 0, 0, 0, '主轴承温度2过高故障', 'var_2014', 'B', 'notdefined', 'var_2014');
INSERT INTO `turbine_model_points` VALUES (349, '20835', 0, 0, 0, 0, '主轴承温度1过高警告', 'var_2015', 'B', 'notdefined', 'var_2015');
INSERT INTO `turbine_model_points` VALUES (350, '20835', 0, 0, 0, 0, '主轴承温度2过高警告', 'var_2016', 'B', 'notdefined', 'var_2016');
INSERT INTO `turbine_model_points` VALUES (351, '20835', 0, 0, 0, 0, '1#叶片轴控柜温度过高故障', 'var_2019', 'B', 'notdefined', 'var_2019');
INSERT INTO `turbine_model_points` VALUES (352, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片轴控柜温度过高故障', 'var_2020', 'B', 'notdefined', 'var_2020');
INSERT INTO `turbine_model_points` VALUES (353, '20835', 0, 0, 0, 0, '2#叶片轴控柜温度过高故障', 'var_2021', 'B', 'notdefined', 'var_2021');
INSERT INTO `turbine_model_points` VALUES (354, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片轴控柜温度过高故障', 'var_2022', 'B', 'notdefined', 'var_2022');
INSERT INTO `turbine_model_points` VALUES (355, '20835', 0, 0, 0, 0, '3#叶片轴控柜温度过高故障', 'var_2023', 'B', 'notdefined', 'var_2023');
INSERT INTO `turbine_model_points` VALUES (356, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片轴控柜温度过高故障', 'var_2024', 'B', 'notdefined', 'var_2024');
INSERT INTO `turbine_model_points` VALUES (357, '20835', 0, 0, 0, 0, '变桨系统检测变桨1#叶片角度太高故障', 'var_2025', 'B', 'notdefined', 'var_2025');
INSERT INTO `turbine_model_points` VALUES (358, '20835', 0, 0, 0, 0, '变桨系统检测变桨1#叶片角度太低故障', 'var_2026', 'B', 'notdefined', 'var_2026');
INSERT INTO `turbine_model_points` VALUES (359, '20835', 0, 0, 0, 0, '变桨1#叶片限位开关2激活故障', 'var_2027', 'B', 'notdefined', 'var_2027');
INSERT INTO `turbine_model_points` VALUES (360, '20835', 0, 0, 0, 0, '变桨1#叶片自检速度过低故障', 'var_2028', 'B', 'notdefined', 'var_2028');
INSERT INTO `turbine_model_points` VALUES (361, '20835', 0, 0, 0, 0, '变桨1#叶片追踪故障', 'var_2029', 'B', 'notdefined', 'var_2029');
INSERT INTO `turbine_model_points` VALUES (362, '20835', 0, 0, 0, 0, '变桨系统检测变桨2#叶片角度太高故障', 'var_2030', 'B', 'notdefined', 'var_2030');
INSERT INTO `turbine_model_points` VALUES (363, '20835', 0, 0, 0, 0, '变桨系统检测变桨2#叶片角度太低故障', 'var_2031', 'B', 'notdefined', 'var_2031');
INSERT INTO `turbine_model_points` VALUES (364, '20835', 0, 0, 0, 0, '变桨2#叶片限位开关2激活故障', 'var_2032', 'B', 'notdefined', 'var_2032');
INSERT INTO `turbine_model_points` VALUES (365, '20835', 0, 0, 0, 0, '变桨2#叶片自检速度过低故障', 'var_2033', 'B', 'notdefined', 'var_2033');
INSERT INTO `turbine_model_points` VALUES (366, '20835', 0, 0, 0, 0, '变桨2#叶片追踪故障', 'var_2034', 'B', 'notdefined', 'var_2034');
INSERT INTO `turbine_model_points` VALUES (367, '20835', 0, 0, 0, 0, '变桨系统检测变桨3#叶片角度太高故障', 'var_2035', 'B', 'notdefined', 'var_2035');
INSERT INTO `turbine_model_points` VALUES (368, '20835', 0, 0, 0, 0, '变桨系统检测变桨3#叶片角度太低故障', 'var_2036', 'B', 'notdefined', 'var_2036');
INSERT INTO `turbine_model_points` VALUES (369, '20835', 0, 0, 0, 0, '变桨3#叶片限位开关2激活故障', 'var_2037', 'B', 'notdefined', 'var_2037');
INSERT INTO `turbine_model_points` VALUES (370, '20835', 0, 0, 0, 0, '变桨3#叶片自检速度过低故障', 'var_2038', 'B', 'notdefined', 'var_2038');
INSERT INTO `turbine_model_points` VALUES (371, '20835', 0, 0, 0, 0, '变桨3#叶片追踪故障', 'var_2039', 'B', 'notdefined', 'var_2039');
INSERT INTO `turbine_model_points` VALUES (372, '20835', 0, 0, 0, 0, '在自检测中1#叶片变桨超级电容电压跌落故障', 'var_2040', 'B', 'notdefined', 'var_2040');
INSERT INTO `turbine_model_points` VALUES (373, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片变桨超级电容电压太低故障', 'var_2041', 'B', 'notdefined', 'var_2041');
INSERT INTO `turbine_model_points` VALUES (374, '20835', 0, 0, 0, 0, '在自检测中2#叶片变桨超级电容电压跌落故障', 'var_2042', 'B', 'notdefined', 'var_2042');
INSERT INTO `turbine_model_points` VALUES (375, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片变桨超级电容电压太低故障', 'var_2043', 'B', 'notdefined', 'var_2043');
INSERT INTO `turbine_model_points` VALUES (376, '20835', 0, 0, 0, 0, '在自检测中3#叶片变桨超级电容电压跌落故障', 'var_2044', 'B', 'notdefined', 'var_2044');
INSERT INTO `turbine_model_points` VALUES (377, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片变桨超级电容电压太低故障', 'var_2045', 'B', 'notdefined', 'var_2045');
INSERT INTO `turbine_model_points` VALUES (378, '20835', 0, 0, 0, 0, '变桨1#叶片超级电容温度过高故障', 'var_2046', 'B', 'notdefined', 'var_2046');
INSERT INTO `turbine_model_points` VALUES (379, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片超级电容温度过高故障', 'var_2047', 'B', 'notdefined', 'var_2047');
INSERT INTO `turbine_model_points` VALUES (380, '20835', 0, 0, 0, 0, '变桨2#叶片超级电容温度过高故障', 'var_2048', 'B', 'notdefined', 'var_2048');
INSERT INTO `turbine_model_points` VALUES (381, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片超级电容温度过高故障', 'var_2049', 'B', 'notdefined', 'var_2049');
INSERT INTO `turbine_model_points` VALUES (382, '20835', 0, 0, 0, 0, '变桨3#叶片超级电容温度过高故障', 'var_2050', 'B', 'notdefined', 'var_2050');
INSERT INTO `turbine_model_points` VALUES (383, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片超级电容温度过高故障', 'var_2051', 'B', 'notdefined', 'var_2051');
INSERT INTO `turbine_model_points` VALUES (384, '20835', 0, 0, 0, 0, '变桨系统检测变桨1#叶片变桨充电器错误故障', 'var_2058', 'B', 'notdefined', 'var_2058');
INSERT INTO `turbine_model_points` VALUES (385, '20835', 0, 0, 0, 0, '变桨系统检测变桨2#叶片变桨充电器错误故障', 'var_2059', 'B', 'notdefined', 'var_2059');
INSERT INTO `turbine_model_points` VALUES (386, '20835', 0, 0, 0, 0, '变桨系统检测变桨3#叶片变桨充电器错误故障', 'var_2060', 'B', 'notdefined', 'var_2060');
INSERT INTO `turbine_model_points` VALUES (387, '20835', 0, 0, 0, 0, '变桨1#叶片通讯故障', 'var_2061', 'B', 'notdefined', 'var_2061');
INSERT INTO `turbine_model_points` VALUES (388, '20835', 0, 0, 0, 0, '1#叶片控制顺序故障', 'var_2064', 'B', 'notdefined', 'var_2064');
INSERT INTO `turbine_model_points` VALUES (389, '20835', 0, 0, 0, 0, '2#叶片控制顺序故障', 'var_2065', 'B', 'notdefined', 'var_2065');
INSERT INTO `turbine_model_points` VALUES (390, '20835', 0, 0, 0, 0, '3#叶片控制顺序故障', 'var_2066', 'B', 'notdefined', 'var_2066');
INSERT INTO `turbine_model_points` VALUES (391, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片变桨控制器温度过高故障', 'var_2067', 'B', 'notdefined', 'var_2067');
INSERT INTO `turbine_model_points` VALUES (392, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片变桨控制器温度过高故障', 'var_2068', 'B', 'notdefined', 'var_2068');
INSERT INTO `turbine_model_points` VALUES (393, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片变桨控制器温度过高故障', 'var_2069', 'B', 'notdefined', 'var_2069');
INSERT INTO `turbine_model_points` VALUES (394, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片变桨驱动器故障', 'var_2070', 'B', 'notdefined', 'var_2070');
INSERT INTO `turbine_model_points` VALUES (395, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片变桨驱动器故障', 'var_2071', 'B', 'notdefined', 'var_2071');
INSERT INTO `turbine_model_points` VALUES (396, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片变桨驱动器故障', 'var_2072', 'B', 'notdefined', 'var_2072');
INSERT INTO `turbine_model_points` VALUES (397, '20835', 0, 0, 0, 0, '变桨系统报出1#叶片变桨急停请求故障', 'var_2073', 'B', 'notdefined', 'var_2073');
INSERT INTO `turbine_model_points` VALUES (398, '20835', 0, 0, 0, 0, '1#叶片编码器偏差警告', 'var_2079', 'B', 'notdefined', 'var_2079');
INSERT INTO `turbine_model_points` VALUES (399, '20835', 0, 0, 0, 0, '2#叶片编码器偏差警告', 'var_2080', 'B', 'notdefined', 'var_2080');
INSERT INTO `turbine_model_points` VALUES (400, '20835', 0, 0, 0, 0, '3#叶片编码器偏差警告', 'var_2081', 'B', 'notdefined', 'var_2081');
INSERT INTO `turbine_model_points` VALUES (401, '20835', 0, 0, 0, 0, '变桨系统报出1#叶片强制手动操作激活故障', 'var_2082', 'B', 'notdefined', 'var_2082');
INSERT INTO `turbine_model_points` VALUES (402, '20835', 0, 0, 0, 0, '变桨轮毂温度1过高故障', 'var_2088', 'B', 'notdefined', 'var_2088');
INSERT INTO `turbine_model_points` VALUES (403, '20835', 0, 0, 0, 0, '变桨轴承润滑系统故障', 'var_2094', 'B', 'notdefined', 'var_2094');
INSERT INTO `turbine_model_points` VALUES (404, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片变桨主控制器没有心跳故障', 'var_2095', 'B', 'notdefined', 'var_2095');
INSERT INTO `turbine_model_points` VALUES (405, '20835', 0, 0, 0, 0, '变桨系统报出1#叶片手动操作激活故障', 'var_2098', 'B', 'notdefined', 'var_2098');
INSERT INTO `turbine_model_points` VALUES (406, '20835', 0, 0, 0, 0, '变桨1#叶片电机温度过高故障', 'var_2103', 'B', 'notdefined', 'var_2103');
INSERT INTO `turbine_model_points` VALUES (407, '20835', 0, 0, 0, 0, '变桨2#叶片电机温度过高故障', 'var_2105', 'B', 'notdefined', 'var_2105');
INSERT INTO `turbine_model_points` VALUES (408, '20835', 0, 0, 0, 0, '变桨3#叶片电机温度过高故障', 'var_2107', 'B', 'notdefined', 'var_2107');
INSERT INTO `turbine_model_points` VALUES (409, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片电机温度过高故障', 'var_2108', 'B', 'notdefined', 'var_2108');
INSERT INTO `turbine_model_points` VALUES (410, '20835', 0, 0, 0, 0, '主控检测1#叶片没有心跳故障', 'var_2109', 'B', 'notdefined', 'var_2109');
INSERT INTO `turbine_model_points` VALUES (411, '20835', 0, 0, 0, 0, '变桨位置不同步故障', 'var_2112', 'B', 'notdefined', 'var_2112');
INSERT INTO `turbine_model_points` VALUES (412, '20835', 0, 0, 0, 0, '变桨系统报出1#叶片安全链断开故障', 'var_2113', 'B', 'notdefined', 'var_2113');
INSERT INTO `turbine_model_points` VALUES (413, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片变桨速度过高故障', 'var_2116', 'B', 'notdefined', 'var_2116');
INSERT INTO `turbine_model_points` VALUES (414, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片变桨速度过高故障', 'var_2117', 'B', 'notdefined', 'var_2117');
INSERT INTO `turbine_model_points` VALUES (415, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片变桨速度过高故障', 'var_2118', 'B', 'notdefined', 'var_2118');
INSERT INTO `turbine_model_points` VALUES (416, '20835', 0, 0, 0, 0, '变桨系统400V电源过载故障', 'var_2119', 'B', 'notdefined', 'var_2119');
INSERT INTO `turbine_model_points` VALUES (417, '20835', 0, 0, 0, 0, '变桨系统重新初始化CAN通讯故障', 'var_2120', 'B', 'notdefined', 'var_2120');
INSERT INTO `turbine_model_points` VALUES (418, '20835', 0, 0, 0, 0, '变桨1#叶片超级电容容量低故障', 'var_2121', 'B', 'notdefined', 'var_2121');
INSERT INTO `turbine_model_points` VALUES (419, '20835', 0, 0, 0, 0, '变桨2#叶片超级电容容量低故障', 'var_2122', 'B', 'notdefined', 'var_2122');
INSERT INTO `turbine_model_points` VALUES (420, '20835', 0, 0, 0, 0, '变桨3#叶片超级电容容量低故障', 'var_2123', 'B', 'notdefined', 'var_2123');
INSERT INTO `turbine_model_points` VALUES (421, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片角度相差太高警告', 'var_2125', 'B', 'notdefined', 'var_2125');
INSERT INTO `turbine_model_points` VALUES (422, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片角度相差太高警告', 'var_2126', 'B', 'notdefined', 'var_2126');
INSERT INTO `turbine_model_points` VALUES (423, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片角度相差太高警告', 'var_2127', 'B', 'notdefined', 'var_2127');
INSERT INTO `turbine_model_points` VALUES (424, '20835', 0, 0, 0, 0, '变桨系统报出主轴承润滑系统故障', 'var_2128', 'B', 'notdefined', 'var_2128');
INSERT INTO `turbine_model_points` VALUES (425, '20835', 0, 0, 0, 0, '变桨齿轮润滑系统报警故障', 'var_2129', 'B', 'notdefined', 'var_2129');
INSERT INTO `turbine_model_points` VALUES (426, '20835', 0, 0, 0, 0, '变桨轴承润滑堵塞警告', 'var_2130', 'B', 'notdefined', 'var_2130');
INSERT INTO `turbine_model_points` VALUES (427, '20835', 0, 0, 0, 0, '变桨系统检测主轴承润滑堵塞警告', 'var_2131', 'B', 'notdefined', 'var_2131');
INSERT INTO `turbine_model_points` VALUES (428, '20835', 0, 0, 0, 0, '变桨齿轮润滑堵塞警告', 'var_2132', 'B', 'notdefined', 'var_2132');
INSERT INTO `turbine_model_points` VALUES (429, '20835', 0, 0, 0, 0, '变桨齿轮润滑油脂液位低警告', 'var_2133', 'B', 'notdefined', 'var_2133');
INSERT INTO `turbine_model_points` VALUES (430, '20835', 0, 0, 0, 0, '变桨轴承润滑油脂液位低警告', 'var_2134', 'B', 'notdefined', 'var_2134');
INSERT INTO `turbine_model_points` VALUES (431, '20835', 0, 0, 0, 0, '主轴承润滑油脂液位低警告', 'var_2135', 'B', 'notdefined', 'var_2135');
INSERT INTO `turbine_model_points` VALUES (432, '20835', 0, 0, 0, 0, '偏航轴承润滑堵塞警告', 'var_2136', 'B', 'notdefined', 'var_2136');
INSERT INTO `turbine_model_points` VALUES (433, '20835', 0, 0, 0, 0, '偏航齿轮润滑堵塞警告', 'var_2137', 'B', 'notdefined', 'var_2137');
INSERT INTO `turbine_model_points` VALUES (434, '20835', 0, 0, 0, 0, '距上次轴承变桨润滑时间太长故障', 'var_2138', 'B', 'notdefined', 'var_2138');
INSERT INTO `turbine_model_points` VALUES (435, '20835', 0, 0, 0, 0, '距上次齿轮变桨润滑时间太长故障', 'var_2139', 'B', 'notdefined', 'var_2139');
INSERT INTO `turbine_model_points` VALUES (436, '20835', 0, 0, 0, 0, '距上次主轴承变桨润滑时间太长故障', 'var_2140', 'B', 'notdefined', 'var_2140');
INSERT INTO `turbine_model_points` VALUES (437, '20835', 0, 0, 0, 0, '变桨1#叶片91度限位开关失效故障', 'var_2141', 'B', 'notdefined', 'var_2141');
INSERT INTO `turbine_model_points` VALUES (438, '20835', 0, 0, 0, 0, '变桨2#叶片91度限位开关失效故障', 'var_2142', 'B', 'notdefined', 'var_2142');
INSERT INTO `turbine_model_points` VALUES (439, '20835', 0, 0, 0, 0, '变桨3#叶片91度限位开关失效故障', 'var_2143', 'B', 'notdefined', 'var_2143');
INSERT INTO `turbine_model_points` VALUES (440, '20835', 0, 0, 0, 0, '变桨1#叶片负3度极限开关触发故障', 'var_2144', 'B', 'notdefined', 'var_2144');
INSERT INTO `turbine_model_points` VALUES (441, '20835', 0, 0, 0, 0, '变桨2#叶片负3度极限开关触发故障', 'var_2145', 'B', 'notdefined', 'var_2145');
INSERT INTO `turbine_model_points` VALUES (442, '20835', 0, 0, 0, 0, '变桨3#叶片负3度极限开关触发故障', 'var_2146', 'B', 'notdefined', 'var_2146');
INSERT INTO `turbine_model_points` VALUES (443, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片电源1温度过高故障', 'var_2147', 'B', 'notdefined', 'var_2147');
INSERT INTO `turbine_model_points` VALUES (444, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片电源1温度过高故障', 'var_2148', 'B', 'notdefined', 'var_2148');
INSERT INTO `turbine_model_points` VALUES (445, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片电源1温度过高故障', 'var_2149', 'B', 'notdefined', 'var_2149');
INSERT INTO `turbine_model_points` VALUES (446, '20835', 0, 0, 0, 0, '发电机NDE轴承超温警告', 'var_2191', 'B', 'notdefined', 'var_2191');
INSERT INTO `turbine_model_points` VALUES (447, '20835', 0, 0, 0, 0, '发电机绕组U1温度过低故障', 'var_2195', 'B', 'notdefined', 'var_2195');
INSERT INTO `turbine_model_points` VALUES (448, '20835', 0, 0, 0, 0, '发电机绕组U2温度过低故障', 'var_2196', 'B', 'notdefined', 'var_2196');
INSERT INTO `turbine_model_points` VALUES (449, '20835', 0, 0, 0, 0, '发电机绕组V1温度过低故障', 'var_2197', 'B', 'notdefined', 'var_2197');
INSERT INTO `turbine_model_points` VALUES (450, '20835', 0, 0, 0, 0, '发电机绕组V2温度过低故障', 'var_2198', 'B', 'notdefined', 'var_2198');
INSERT INTO `turbine_model_points` VALUES (451, '20835', 0, 0, 0, 0, '发电机绕组W1温度过低故障', 'var_2199', 'B', 'notdefined', 'var_2199');
INSERT INTO `turbine_model_points` VALUES (452, '20835', 0, 0, 0, 0, '发电机绕组W2温度过低故障', 'var_2200', 'B', 'notdefined', 'var_2200');
INSERT INTO `turbine_model_points` VALUES (453, '20835', 0, 0, 0, 0, '发电机绕组U1温度高警告', 'var_2203', 'B', 'notdefined', 'var_2203');
INSERT INTO `turbine_model_points` VALUES (454, '20835', 0, 0, 0, 0, '发电机绕组U1温度低警告', 'var_2204', 'B', 'notdefined', 'var_2204');
INSERT INTO `turbine_model_points` VALUES (455, '20835', 0, 0, 0, 0, '发电机绕组U2温度低警告', 'var_2205', 'B', 'notdefined', 'var_2205');
INSERT INTO `turbine_model_points` VALUES (456, '20835', 0, 0, 0, 0, '发电机绕组V1温度低警告', 'var_2206', 'B', 'notdefined', 'var_2206');
INSERT INTO `turbine_model_points` VALUES (457, '20835', 0, 0, 0, 0, '发电机绕组V2温度低警告', 'var_2207', 'B', 'notdefined', 'var_2207');
INSERT INTO `turbine_model_points` VALUES (458, '20835', 0, 0, 0, 0, '发电机绕组W1温度低警告', 'var_2208', 'B', 'notdefined', 'var_2208');
INSERT INTO `turbine_model_points` VALUES (459, '20835', 0, 0, 0, 0, '发电机绕组W2温度低警告', 'var_2209', 'B', 'notdefined', 'var_2209');
INSERT INTO `turbine_model_points` VALUES (460, '20835', 0, 0, 0, 0, '发电机绕组V1温度高警告', 'var_2210', 'B', 'notdefined', 'var_2210');
INSERT INTO `turbine_model_points` VALUES (461, '20835', 0, 0, 0, 0, '发电机绕组W1温度高警告', 'var_2211', 'B', 'notdefined', 'var_2211');
INSERT INTO `turbine_model_points` VALUES (462, '20835', 0, 0, 0, 0, '发电机润滑报警故障', 'var_2212', 'B', 'notdefined', 'var_2212');
INSERT INTO `turbine_model_points` VALUES (463, '20835', 0, 0, 0, 0, '发电机主滑环故障', 'var_2213', 'B', 'notdefined', 'var_2213');
INSERT INTO `turbine_model_points` VALUES (464, '20835', 0, 0, 0, 0, '发电机加热器过载故障', 'var_2214', 'B', 'notdefined', 'var_2214');
INSERT INTO `turbine_model_points` VALUES (465, '20835', 0, 0, 0, 0, '发电机功率曲线超上限故障', 'var_2216', 'B', 'notdefined', 'var_2216');
INSERT INTO `turbine_model_points` VALUES (466, '20835', 0, 0, 0, 0, '发电机发电功率超高故障', 'var_2217', 'B', 'notdefined', 'var_2217');
INSERT INTO `turbine_model_points` VALUES (467, '20835', 0, 0, 0, 0, '发电机DE端接地碳刷磨损故障', 'var_2220', 'B', 'notdefined', 'var_2220');
INSERT INTO `turbine_model_points` VALUES (468, '20835', 0, 0, 0, 0, '发电机过压Crowbar激活故障', 'var_2221', 'B', 'notdefined', 'var_2221');
INSERT INTO `turbine_model_points` VALUES (469, '20835', 0, 0, 0, 0, '发电机滑环温度过高故障', 'var_2222', 'B', 'notdefined', 'var_2222');
INSERT INTO `turbine_model_points` VALUES (470, '20835', 0, 0, 0, 0, '发电机冷却水入口温度低警告', 'var_2225', 'B', 'notdefined', 'var_2225');
INSERT INTO `turbine_model_points` VALUES (471, '20835', 0, 0, 0, 0, '发电机冷却水入口温度高警告', 'var_2226', 'B', 'notdefined', 'var_2226');
INSERT INTO `turbine_model_points` VALUES (472, '20835', 0, 0, 0, 0, '发电机滑环温度高警告', 'var_2227', 'B', 'notdefined', 'var_2227');
INSERT INTO `turbine_model_points` VALUES (473, '20835', 0, 0, 0, 0, '发电机电机加热器过载故障', 'var_2228', 'B', 'notdefined', 'var_2228');
INSERT INTO `turbine_model_points` VALUES (474, '20835', 0, 0, 0, 0, '发电机内部冷却风扇1过载故障', 'var_2230', 'B', 'notdefined', 'var_2230');
INSERT INTO `turbine_model_points` VALUES (475, '20835', 0, 0, 0, 0, '发电机内部冷却风扇2过载故障', 'var_2231', 'B', 'notdefined', 'var_2231');
INSERT INTO `turbine_model_points` VALUES (476, '20835', 0, 0, 0, 0, '发电机冷却液加热器过载故障', 'var_2232', 'B', 'notdefined', 'var_2232');
INSERT INTO `turbine_model_points` VALUES (477, '20835', 0, 0, 0, 0, '发电机绕组U2温度高警告', 'var_2237', 'B', 'notdefined', 'var_2237');
INSERT INTO `turbine_model_points` VALUES (478, '20835', 0, 0, 0, 0, '发电机绕组V2温度高警告', 'var_2238', 'B', 'notdefined', 'var_2238');
INSERT INTO `turbine_model_points` VALUES (479, '20835', 0, 0, 0, 0, '发电机绕组W2温度高警告', 'var_2239', 'B', 'notdefined', 'var_2239');
INSERT INTO `turbine_model_points` VALUES (480, '20835', 0, 0, 0, 0, '发电机冷却液流速太低故障', 'var_2240', 'B', 'notdefined', 'var_2240');
INSERT INTO `turbine_model_points` VALUES (481, '20835', 0, 0, 0, 0, '发电机冷却空气入口1温度太高故障', 'var_2241', 'B', 'notdefined', 'var_2241');
INSERT INTO `turbine_model_points` VALUES (482, '20835', 0, 0, 0, 0, '发电机冷却空气入口2温度太高故障', 'var_2242', 'B', 'notdefined', 'var_2242');
INSERT INTO `turbine_model_points` VALUES (483, '20835', 0, 0, 0, 0, '发电机冷却空气出口温度太高故障', 'var_2243', 'B', 'notdefined', 'var_2243');
INSERT INTO `turbine_model_points` VALUES (484, '20835', 0, 0, 0, 0, '发电机冷却空气入口1温度高警告', 'var_2244', 'B', 'notdefined', 'var_2244');
INSERT INTO `turbine_model_points` VALUES (485, '20835', 0, 0, 0, 0, '发电机冷却空气入口2温度高警告', 'var_2245', 'B', 'notdefined', 'var_2245');
INSERT INTO `turbine_model_points` VALUES (486, '20835', 0, 0, 0, 0, '发电机冷却空气出口温度高警告', 'var_2246', 'B', 'notdefined', 'var_2246');
INSERT INTO `turbine_model_points` VALUES (487, '20835', 0, 0, 0, 0, '发电机冷却液压力太低故障', 'var_2247', 'B', 'notdefined', 'var_2247');
INSERT INTO `turbine_model_points` VALUES (488, '20835', 0, 0, 0, 0, '发电机冷却液压力太高故障', 'var_2248', 'B', 'notdefined', 'var_2248');
INSERT INTO `turbine_model_points` VALUES (489, '20835', 0, 0, 0, 0, '发电机冷却液压力太低警告', 'var_2249', 'B', 'notdefined', 'var_2249');
INSERT INTO `turbine_model_points` VALUES (490, '20835', 0, 0, 0, 0, '发电机冷却液压力太高警告', 'var_2250', 'B', 'notdefined', 'var_2250');
INSERT INTO `turbine_model_points` VALUES (491, '20835', 0, 0, 0, 0, '发电机无效参数配置故障', 'var_2251', 'B', 'notdefined', 'var_2251');
INSERT INTO `turbine_model_points` VALUES (492, '20835', 0, 0, 0, 0, '发电机防雷器1故障', 'var_2253', 'B', 'notdefined', 'var_2253');
INSERT INTO `turbine_model_points` VALUES (493, '20835', 0, 0, 0, 0, '发电机防雷器2故障', 'var_2254', 'B', 'notdefined', 'var_2254');
INSERT INTO `turbine_model_points` VALUES (494, '20835', 0, 0, 0, 0, '发电机NDE端接地碳刷磨损故障', 'var_2255', 'B', 'notdefined', 'var_2255');
INSERT INTO `turbine_model_points` VALUES (495, '20835', 0, 0, 0, 0, 'UPS供电失效故障', 'var_2260', 'B', 'notdefined', 'var_2260');
INSERT INTO `turbine_model_points` VALUES (496, '20835', 0, 0, 0, 0, 'UPS关断故障', 'var_2261', 'B', 'notdefined', 'var_2261');
INSERT INTO `turbine_model_points` VALUES (497, '20835', 0, 0, 0, 0, '远程手动停机故障', 'var_2262', 'B', 'notdefined', 'var_2262');
INSERT INTO `turbine_model_points` VALUES (498, '20835', 0, 0, 0, 0, '本地手动停机故障', 'var_2263', 'B', 'notdefined', 'var_2263');
INSERT INTO `turbine_model_points` VALUES (499, '20835', 0, 0, 0, 0, '中压断路器切出故障', 'var_2264', 'B', 'notdefined', 'var_2264');
INSERT INTO `turbine_model_points` VALUES (500, '20835', 0, 0, 0, 0, '箱变温度太高故障', 'var_2266', 'B', 'notdefined', 'var_2266');
INSERT INTO `turbine_model_points` VALUES (501, '20835', 0, 0, 0, 0, '箱变温度警告', 'var_2267', 'B', 'notdefined', 'var_2267');
INSERT INTO `turbine_model_points` VALUES (502, '20835', 0, 0, 0, 0, '箱变油压开关激活故障', 'var_2268', 'B', 'notdefined', 'var_2268');
INSERT INTO `turbine_model_points` VALUES (503, '20835', 0, 0, 0, 0, '中压断路器错误故障', 'var_2269', 'B', 'notdefined', 'var_2269');
INSERT INTO `turbine_model_points` VALUES (504, '20835', 0, 0, 0, 0, '箱变温度警告（DI测量）', 'var_2270', 'B', 'notdefined', 'var_2270');
INSERT INTO `turbine_model_points` VALUES (505, '20835', 0, 0, 0, 0, '箱变冷却液入口温度高故障', 'var_2271', 'B', 'notdefined', 'var_2271');
INSERT INTO `turbine_model_points` VALUES (506, '20835', 0, 0, 0, 0, '箱变冷却液入口温度高警告', 'var_2272', 'B', 'notdefined', 'var_2272');
INSERT INTO `turbine_model_points` VALUES (507, '20835', 0, 0, 0, 0, '箱变冷却液出口温度高故障', 'var_2273', 'B', 'notdefined', 'var_2273');
INSERT INTO `turbine_model_points` VALUES (508, '20835', 0, 0, 0, 0, '箱变冷却液出口温度高警告', 'var_2274', 'B', 'notdefined', 'var_2274');
INSERT INTO `turbine_model_points` VALUES (509, '20835', 0, 0, 0, 0, '箱变冷却液入口压力高故障', 'var_2275', 'B', 'notdefined', 'var_2275');
INSERT INTO `turbine_model_points` VALUES (510, '20835', 0, 0, 0, 0, '箱变冷却液入口压力高警告', 'var_2276', 'B', 'notdefined', 'var_2276');
INSERT INTO `turbine_model_points` VALUES (511, '20835', 0, 0, 0, 0, '箱变供电过载故障', 'var_2277', 'B', 'notdefined', 'var_2277');
INSERT INTO `turbine_model_points` VALUES (512, '20835', 0, 0, 0, 0, '箱变冷却风扇过载故障', 'var_2278', 'B', 'notdefined', 'var_2278');
INSERT INTO `turbine_model_points` VALUES (513, '20835', 0, 0, 0, 0, '箱变升压器冷却装置故障', 'var_2279', 'B', 'notdefined', 'var_2279');
INSERT INTO `turbine_model_points` VALUES (514, '20835', 0, 0, 0, 0, '箱变升压器工作电源丢失故障', 'var_2280', 'B', 'notdefined', 'var_2280');
INSERT INTO `turbine_model_points` VALUES (515, '20835', 0, 0, 0, 0, '箱变冷去风扇备用加热器过载故障', 'var_2281', 'B', 'notdefined', 'var_2281');
INSERT INTO `turbine_model_points` VALUES (516, '20835', 0, 0, 0, 0, '箱变冷却泵电机过载故障', 'var_2282', 'B', 'notdefined', 'var_2282');
INSERT INTO `turbine_model_points` VALUES (517, '20835', 0, 0, 0, 0, '箱变温度报警故障', 'var_2283', 'B', 'notdefined', 'var_2283');
INSERT INTO `turbine_model_points` VALUES (518, '20835', 0, 0, 0, 0, '箱变绕组U1温度高警告', 'var_2284', 'B', 'notdefined', 'var_2284');
INSERT INTO `turbine_model_points` VALUES (519, '20835', 0, 0, 0, 0, '箱变绕组V1温度高警告', 'var_2285', 'B', 'notdefined', 'var_2285');
INSERT INTO `turbine_model_points` VALUES (520, '20835', 0, 0, 0, 0, '箱变绕组W1温度高警告', 'var_2286', 'B', 'notdefined', 'var_2286');
INSERT INTO `turbine_model_points` VALUES (521, '20835', 0, 0, 0, 0, '箱变绕组U1温度高故障', 'var_2287', 'B', 'notdefined', 'var_2287');
INSERT INTO `turbine_model_points` VALUES (522, '20835', 0, 0, 0, 0, '箱变绕组V1温度高故障', 'var_2288', 'B', 'notdefined', 'var_2288');
INSERT INTO `turbine_model_points` VALUES (523, '20835', 0, 0, 0, 0, '箱变绕组W1温度高故障', 'var_2289', 'B', 'notdefined', 'var_2289');
INSERT INTO `turbine_model_points` VALUES (524, '20835', 0, 0, 0, 0, '箱变冷却液入口压力低故障', 'var_2290', 'B', 'notdefined', 'var_2290');
INSERT INTO `turbine_model_points` VALUES (525, '20835', 0, 0, 0, 0, '箱变冷却液入口压力低警告', 'var_2291', 'B', 'notdefined', 'var_2291');
INSERT INTO `turbine_model_points` VALUES (526, '20835', 0, 0, 0, 0, '中压系统无效配置故障', 'var_2292', 'B', 'notdefined', 'var_2292');
INSERT INTO `turbine_model_points` VALUES (527, '20835', 0, 0, 0, 0, '箱变升压器门打开故障', 'var_2293', 'B', 'notdefined', 'var_2293');
INSERT INTO `turbine_model_points` VALUES (528, '20835', 0, 0, 0, 0, '主断路器异常动作故障', 'var_2294', 'B', 'notdefined', 'var_2294');
INSERT INTO `turbine_model_points` VALUES (529, '20835', 0, 0, 0, 0, 'SCADA远程断开C1柜', 'var_2295', 'B', 'notdefined', 'var_2295');
INSERT INTO `turbine_model_points` VALUES (530, '20835', 0, 0, 0, 0, 'SCADA远程断开C2柜', 'var_2296', 'B', 'notdefined', 'var_2296');
INSERT INTO `turbine_model_points` VALUES (531, '20835', 0, 0, 0, 0, 'SCADA远程断开V柜', 'var_2297', 'B', 'notdefined', 'var_2297');
INSERT INTO `turbine_model_points` VALUES (532, '20835', 0, 0, 0, 0, '变频器1控制序列错误故障', 'var_2299', 'B', 'notdefined', 'var_2299');
INSERT INTO `turbine_model_points` VALUES (533, '20835', 0, 0, 0, 0, '变频器1冷却液入口压力高警告', 'var_2300', 'B', 'notdefined', 'var_2300');
INSERT INTO `turbine_model_points` VALUES (534, '20835', 0, 0, 0, 0, '变频器1冷却液入口压力低警告', 'var_2301', 'B', 'notdefined', 'var_2301');
INSERT INTO `turbine_model_points` VALUES (535, '20835', 0, 0, 0, 0, '变频器1冷却液入口压力过高故障', 'var_2302', 'B', 'notdefined', 'var_2302');
INSERT INTO `turbine_model_points` VALUES (536, '20835', 0, 0, 0, 0, '变频器1冷却液入口压力过低故障', 'var_2303', 'B', 'notdefined', 'var_2303');
INSERT INTO `turbine_model_points` VALUES (537, '20835', 0, 0, 0, 0, '变频器1冷却液入口温度高警告', 'var_2304', 'B', 'notdefined', 'var_2304');
INSERT INTO `turbine_model_points` VALUES (538, '20835', 0, 0, 0, 0, '变频器1冷却液入口温度低警告', 'var_2305', 'B', 'notdefined', 'var_2305');
INSERT INTO `turbine_model_points` VALUES (539, '20835', 0, 0, 0, 0, '变频器1冷却液入口温度过高故障', 'var_2306', 'B', 'notdefined', 'var_2306');
INSERT INTO `turbine_model_points` VALUES (540, '20835', 0, 0, 0, 0, '变频器1冷却液入口温度过低故障', 'var_2307', 'B', 'notdefined', 'var_2307');
INSERT INTO `turbine_model_points` VALUES (541, '20835', 0, 0, 0, 0, '变频器1冷却液泵电机过载故障', 'var_2308', 'B', 'notdefined', 'var_2308');
INSERT INTO `turbine_model_points` VALUES (542, '20835', 0, 0, 0, 0, '变频器1冷却风扇过载故障', 'var_2309', 'B', 'notdefined', 'var_2309');
INSERT INTO `turbine_model_points` VALUES (543, '20835', 0, 0, 0, 0, '变频器1故障激活故障', 'var_2310', 'B', 'notdefined', 'var_2310');
INSERT INTO `turbine_model_points` VALUES (544, '20835', 0, 0, 0, 0, '变频器1发电机速度传感器错误故障', 'var_2311', 'B', 'notdefined', 'var_2311');
INSERT INTO `turbine_model_points` VALUES (545, '20835', 0, 0, 0, 0, '变频器1加热过载故障', 'var_2312', 'B', 'notdefined', 'var_2312');
INSERT INTO `turbine_model_points` VALUES (546, '20835', 0, 0, 0, 0, '变频器1看门狗信号丢失故障', 'var_2314', 'B', 'notdefined', 'var_2314');
INSERT INTO `turbine_model_points` VALUES (547, '20835', 0, 0, 0, 0, '变频器2冷却液入口压力高警告', 'var_2317', 'B', 'notdefined', 'var_2317');
INSERT INTO `turbine_model_points` VALUES (548, '20835', 0, 0, 0, 0, '变频器2冷却液入口压力低警告', 'var_2318', 'B', 'notdefined', 'var_2318');
INSERT INTO `turbine_model_points` VALUES (549, '20835', 0, 0, 0, 0, '变频器2冷却液入口压力过高故障', 'var_2319', 'B', 'notdefined', 'var_2319');
INSERT INTO `turbine_model_points` VALUES (550, '20835', 0, 0, 0, 0, '变频器2冷却液入口压力过低故障', 'var_2320', 'B', 'notdefined', 'var_2320');
INSERT INTO `turbine_model_points` VALUES (551, '20835', 0, 0, 0, 0, '变频器2冷却液入口温度高警告', 'var_2321', 'B', 'notdefined', 'var_2321');
INSERT INTO `turbine_model_points` VALUES (552, '20835', 0, 0, 0, 0, '变频器2冷却液入口温度低警告', 'var_2322', 'B', 'notdefined', 'var_2322');
INSERT INTO `turbine_model_points` VALUES (553, '20835', 0, 0, 0, 0, '变频器2冷却液入口温度过高故障', 'var_2323', 'B', 'notdefined', 'var_2323');
INSERT INTO `turbine_model_points` VALUES (554, '20835', 0, 0, 0, 0, '变频器2冷却液入口温度过低故障', 'var_2324', 'B', 'notdefined', 'var_2324');
INSERT INTO `turbine_model_points` VALUES (555, '20835', 0, 0, 0, 0, '频器2冷却液泵电机过载故障', 'var_2325', 'B', 'notdefined', 'var_2325');
INSERT INTO `turbine_model_points` VALUES (556, '20835', 0, 0, 0, 0, '变频器2冷却风扇过载故障', 'var_2326', 'B', 'notdefined', 'var_2326');
INSERT INTO `turbine_model_points` VALUES (557, '20835', 0, 0, 0, 0, '变频器2故障激活故障', 'var_2327', 'B', 'notdefined', 'var_2327');
INSERT INTO `turbine_model_points` VALUES (558, '20835', 0, 0, 0, 0, '变频器2加热过载故障', 'var_2329', 'B', 'notdefined', 'var_2329');
INSERT INTO `turbine_model_points` VALUES (559, '20835', 0, 0, 0, 0, '变频器3冷却液入口压力高警告', 'var_2332', 'B', 'notdefined', 'var_2332');
INSERT INTO `turbine_model_points` VALUES (560, '20835', 0, 0, 0, 0, '变频器3冷却液入口压力低警告', 'var_2333', 'B', 'notdefined', 'var_2333');
INSERT INTO `turbine_model_points` VALUES (561, '20835', 0, 0, 0, 0, '变频器3冷却液入口压力过高故障', 'var_2334', 'B', 'notdefined', 'var_2334');
INSERT INTO `turbine_model_points` VALUES (562, '20835', 0, 0, 0, 0, '变频器3冷却液入口压力过低故障', 'var_2335', 'B', 'notdefined', 'var_2335');
INSERT INTO `turbine_model_points` VALUES (563, '20835', 0, 0, 0, 0, '变频器3冷却液入口温度高警告', 'var_2336', 'B', 'notdefined', 'var_2336');
INSERT INTO `turbine_model_points` VALUES (564, '20835', 0, 0, 0, 0, '变频器3冷却液入口温度低警告', 'var_2337', 'B', 'notdefined', 'var_2337');
INSERT INTO `turbine_model_points` VALUES (565, '20835', 0, 0, 0, 0, '变频器3冷却液入口温度过高故障', 'var_2338', 'B', 'notdefined', 'var_2338');
INSERT INTO `turbine_model_points` VALUES (566, '20835', 0, 0, 0, 0, '频器器3冷却液入口温度过低故障', 'var_2339', 'B', 'notdefined', 'var_2339');
INSERT INTO `turbine_model_points` VALUES (567, '20835', 0, 0, 0, 0, '变频器3冷却液泵电机过载故障', 'var_2340', 'B', 'notdefined', 'var_2340');
INSERT INTO `turbine_model_points` VALUES (568, '20835', 0, 0, 0, 0, '变频器3冷却风扇过载故障', 'var_2341', 'B', 'notdefined', 'var_2341');
INSERT INTO `turbine_model_points` VALUES (569, '20835', 0, 0, 0, 0, '变频器3加热过载故障', 'var_2342', 'B', 'notdefined', 'var_2342');
INSERT INTO `turbine_model_points` VALUES (570, '20835', 0, 0, 0, 0, '变频器4冷却液入口压力高警告', 'var_2343', 'B', 'notdefined', 'var_2343');
INSERT INTO `turbine_model_points` VALUES (571, '20835', 0, 0, 0, 0, '变频器4冷却液入口压力低警告', 'var_2344', 'B', 'notdefined', 'var_2344');
INSERT INTO `turbine_model_points` VALUES (572, '20835', 0, 0, 0, 0, '变频器4冷却液入口压力过高故障', 'var_2345', 'B', 'notdefined', 'var_2345');
INSERT INTO `turbine_model_points` VALUES (573, '20835', 0, 0, 0, 0, '变频器4冷却液入口压力过低故障', 'var_2346', 'B', 'notdefined', 'var_2346');
INSERT INTO `turbine_model_points` VALUES (574, '20835', 0, 0, 0, 0, '变频器4冷却液入口温度高警告', 'var_2347', 'B', 'notdefined', 'var_2347');
INSERT INTO `turbine_model_points` VALUES (575, '20835', 0, 0, 0, 0, '变频器4冷却液入口温度低警告', 'var_2348', 'B', 'notdefined', 'var_2348');
INSERT INTO `turbine_model_points` VALUES (576, '20835', 0, 0, 0, 0, '变频器4冷却液入口温度过高故障', 'var_2349', 'B', 'notdefined', 'var_2349');
INSERT INTO `turbine_model_points` VALUES (577, '20835', 0, 0, 0, 0, '变频器4冷却液入口温度过低故障', 'var_2350', 'B', 'notdefined', 'var_2350');
INSERT INTO `turbine_model_points` VALUES (578, '20835', 0, 0, 0, 0, '变频器4冷却液泵电机过载故障', 'var_2351', 'B', 'notdefined', 'var_2351');
INSERT INTO `turbine_model_points` VALUES (579, '20835', 0, 0, 0, 0, '变频器4冷却风扇过载故障', 'var_2352', 'B', 'notdefined', 'var_2352');
INSERT INTO `turbine_model_points` VALUES (580, '20835', 0, 0, 0, 0, '变频器4加热过载故障', 'var_2353', 'B', 'notdefined', 'var_2353');
INSERT INTO `turbine_model_points` VALUES (581, '20835', 0, 0, 0, 0, '变频器通讯错误故障', 'var_2354', 'B', 'notdefined', 'var_2354');
INSERT INTO `turbine_model_points` VALUES (582, '20835', 0, 0, 0, 0, '变频器通讯重新初始化故障', 'var_2355', 'B', 'notdefined', 'var_2355');
INSERT INTO `turbine_model_points` VALUES (583, '20835', 0, 0, 0, 0, '变频器电源过载故障', 'var_2356', 'B', 'notdefined', 'var_2356');
INSERT INTO `turbine_model_points` VALUES (584, '20835', 0, 0, 0, 0, '发电机机械速度太高故障', 'var_2357', 'B', 'notdefined', 'var_2357');
INSERT INTO `turbine_model_points` VALUES (585, '20835', 0, 0, 0, 0, '发电机机械速度太低故障', 'var_2358', 'B', 'notdefined', 'var_2358');
INSERT INTO `turbine_model_points` VALUES (586, '20835', 0, 0, 0, 0, '变频器1失能警告', 'var_2359', 'B', 'notdefined', 'var_2359');
INSERT INTO `turbine_model_points` VALUES (587, '20835', 0, 0, 0, 0, '变频器2失能警告', 'var_2360', 'B', 'notdefined', 'var_2360');
INSERT INTO `turbine_model_points` VALUES (588, '20835', 0, 0, 0, 0, '变频器LVRT激活故障', 'var_2361', 'B', 'notdefined', 'var_2361');
INSERT INTO `turbine_model_points` VALUES (589, '20835', 0, 0, 0, 0, '液压系统无效配置故障', 'var_2362', 'B', 'notdefined', 'var_2362');
INSERT INTO `turbine_model_points` VALUES (590, '20835', 0, 0, 0, 0, '液压系统油位1低故障', 'var_2363', 'B', 'notdefined', 'var_2363');
INSERT INTO `turbine_model_points` VALUES (591, '20835', 0, 0, 0, 0, '液压系统油温1太高故障', 'var_2365', 'B', 'notdefined', 'var_2365');
INSERT INTO `turbine_model_points` VALUES (592, '20835', 0, 0, 0, 0, '液压泵电机1过载故障', 'var_2369', 'B', 'notdefined', 'var_2369');
INSERT INTO `turbine_model_points` VALUES (593, '20835', 0, 0, 0, 0, '偏航液压刹车高压力太低故障', 'var_2371', 'B', 'notdefined', 'var_2371');
INSERT INTO `turbine_model_points` VALUES (594, '20835', 0, 0, 0, 0, '偏航液压刹车压力未达到低压压力故障', 'var_2372', 'B', 'notdefined', 'var_2372');
INSERT INTO `turbine_model_points` VALUES (595, '20835', 0, 0, 0, 0, '偏航液压刹车低压力太低故障', 'var_2373', 'B', 'notdefined', 'var_2373');
INSERT INTO `turbine_model_points` VALUES (596, '20835', 0, 0, 0, 0, '偏航液压刹车未释放故障', 'var_2374', 'B', 'notdefined', 'var_2374');
INSERT INTO `turbine_model_points` VALUES (597, '20835', 0, 0, 0, 0, '紧急停机开关激活故障', 'var_2375', 'B', 'notdefined', 'var_2375');
INSERT INTO `turbine_model_points` VALUES (598, '20835', 0, 0, 0, 0, '加速度1超最大值故障', 'var_2377', 'B', 'notdefined', 'var_2377');
INSERT INTO `turbine_model_points` VALUES (599, '20835', 0, 0, 0, 0, '加速度2超最大值故障', 'var_2378', 'B', 'notdefined', 'var_2378');
INSERT INTO `turbine_model_points` VALUES (600, '20835', 0, 0, 0, 0, '安全控制器错误故障', 'var_2379', 'B', 'notdefined', 'var_2379');
INSERT INTO `turbine_model_points` VALUES (601, '20835', 0, 0, 0, 0, '机舱振动1瞬时值超限故障', 'var_2380', 'B', 'notdefined', 'var_2380');
INSERT INTO `turbine_model_points` VALUES (602, '20835', 0, 0, 0, 0, '速度传感器错误故障', 'var_2385', 'B', 'notdefined', 'var_2385');
INSERT INTO `turbine_model_points` VALUES (603, '20835', 0, 0, 0, 0, '安全控制器软件版本无效故障', 'var_2388', 'B', 'notdefined', 'var_2388');
INSERT INTO `turbine_model_points` VALUES (604, '20835', 0, 0, 0, 0, '机舱振动2瞬时值超限故障', 'var_2389', 'B', 'notdefined', 'var_2389');
INSERT INTO `turbine_model_points` VALUES (605, '20835', 0, 0, 0, 0, '转子反向超速警告', 'var_2390', 'B', 'notdefined', 'var_2390');
INSERT INTO `turbine_model_points` VALUES (606, '20835', 0, 0, 0, 0, '发电机反向超速警告', 'var_2391', 'B', 'notdefined', 'var_2391');
INSERT INTO `turbine_model_points` VALUES (607, '20835', 0, 0, 0, 0, '安全控制器无效类型故障', 'var_2394', 'B', 'notdefined', 'var_2394');
INSERT INTO `turbine_model_points` VALUES (608, '20835', 0, 0, 0, 0, '安全控制器版本验证正在进行故障', 'var_2395', 'B', 'notdefined', 'var_2395');
INSERT INTO `turbine_model_points` VALUES (609, '20835', 0, 0, 0, 0, '没有选择转子转速故障', 'var_2397', 'B', 'notdefined', 'var_2397');
INSERT INTO `turbine_model_points` VALUES (610, '20835', 0, 0, 0, 0, '转子反向超速事件类型没有选择故障', 'var_2399', 'B', 'notdefined', 'var_2399');
INSERT INTO `turbine_model_points` VALUES (611, '20835', 0, 0, 0, 0, '机舱振动2的10min平均值超限故障', 'var_2400', 'B', 'notdefined', 'var_2400');
INSERT INTO `turbine_model_points` VALUES (612, '20835', 0, 0, 0, 0, '发电机机械速度无效配置故障', 'var_2401', 'B', 'notdefined', 'var_2401');
INSERT INTO `turbine_model_points` VALUES (613, '20835', 0, 0, 0, 0, '转子加速度最大值超限故障', 'var_2403', 'B', 'notdefined', 'var_2403');
INSERT INTO `turbine_model_points` VALUES (614, '20835', 0, 0, 0, 0, '安全系统无效配置故障', 'var_2404', 'B', 'notdefined', 'var_2404');
INSERT INTO `turbine_model_points` VALUES (615, '20835', 0, 0, 0, 0, '转子刹车无效配置故障', 'var_2405', 'B', 'notdefined', 'var_2405');
INSERT INTO `turbine_model_points` VALUES (616, '20835', 0, 0, 0, 0, '转子刹车1应用状态时压力太低故障', 'var_2406', 'B', 'notdefined', 'var_2406');
INSERT INTO `turbine_model_points` VALUES (617, '20835', 0, 0, 0, 0, '转子刹车1释放状态时油压太高故障', 'var_2407', 'B', 'notdefined', 'var_2407');
INSERT INTO `turbine_model_points` VALUES (618, '20835', 0, 0, 0, 0, '转子刹车1储压罐压力太低故障', 'var_2408', 'B', 'notdefined', 'var_2408');
INSERT INTO `turbine_model_points` VALUES (619, '20835', 0, 0, 0, 0, '转子刹车1刹车盘磨损故障', 'var_2409', 'B', 'notdefined', 'var_2409');
INSERT INTO `turbine_model_points` VALUES (620, '20835', 0, 0, 0, 0, '转子刹车1刹车盘预磨损警告', 'var_2410', 'B', 'notdefined', 'var_2410');
INSERT INTO `turbine_model_points` VALUES (621, '20835', 0, 0, 0, 0, '转子锁未释放故障', 'var_2417', 'B', 'notdefined', 'var_2417');
INSERT INTO `turbine_model_points` VALUES (622, '20835', 0, 0, 0, 0, '辅助电源变压器绕组温度高警告', 'var_2418', 'B', 'notdefined', 'var_2418');
INSERT INTO `turbine_model_points` VALUES (623, '20835', 0, 0, 0, 0, '辅助电源变压器绕组温度太高故障', 'var_2420', 'B', 'notdefined', 'var_2420');
INSERT INTO `turbine_model_points` VALUES (624, '20835', 0, 0, 0, 0, 'A11控制柜温度1（左边）高警告', 'var_2434', 'B', 'notdefined', 'var_2434');
INSERT INTO `turbine_model_points` VALUES (625, '20835', 0, 0, 0, 0, 'A11控制柜温度1（左边）低警告', 'var_2435', 'B', 'notdefined', 'var_2435');
INSERT INTO `turbine_model_points` VALUES (626, '20835', 0, 0, 0, 0, 'A11控制柜温度1（左边）太高故障', 'var_2436', 'B', 'notdefined', 'var_2436');
INSERT INTO `turbine_model_points` VALUES (627, '20835', 0, 0, 0, 0, 'A11控制柜温度1（左边）太低故障', 'var_2437', 'B', 'notdefined', 'var_2437');
INSERT INTO `turbine_model_points` VALUES (628, '20835', 0, 0, 0, 0, 'A11控制柜温度2（右边）高警告', 'var_2438', 'B', 'notdefined', 'var_2438');
INSERT INTO `turbine_model_points` VALUES (629, '20835', 0, 0, 0, 0, 'A11控制柜温度2（右边）低警告', 'var_2439', 'B', 'notdefined', 'var_2439');
INSERT INTO `turbine_model_points` VALUES (630, '20835', 0, 0, 0, 0, 'A11控制柜温度2（右边）太高故障', 'var_2440', 'B', 'notdefined', 'var_2440');
INSERT INTO `turbine_model_points` VALUES (631, '20835', 0, 0, 0, 0, 'A11控制柜温度2（右边）太低故障', 'var_2441', 'B', 'notdefined', 'var_2441');
INSERT INTO `turbine_model_points` VALUES (632, '20835', 0, 0, 0, 0, 'A30控制柜温度1（左边）高警告', 'var_2442', 'B', 'notdefined', 'var_2442');
INSERT INTO `turbine_model_points` VALUES (633, '20835', 0, 0, 0, 0, 'A30控制柜温度1（左边）低警告', 'var_2443', 'B', 'notdefined', 'var_2443');
INSERT INTO `turbine_model_points` VALUES (634, '20835', 0, 0, 0, 0, 'A30控制柜温度1（左边）太高故障', 'var_2444', 'B', 'notdefined', 'var_2444');
INSERT INTO `turbine_model_points` VALUES (635, '20835', 0, 0, 0, 0, 'A30控制柜温度1（左边）太低故障', 'var_2445', 'B', 'notdefined', 'var_2445');
INSERT INTO `turbine_model_points` VALUES (636, '20835', 0, 0, 0, 0, 'A30控制柜温度2（右边）高警告', 'var_2446', 'B', 'notdefined', 'var_2446');
INSERT INTO `turbine_model_points` VALUES (637, '20835', 0, 0, 0, 0, 'A30控制柜温度2（右边）低警告', 'var_2447', 'B', 'notdefined', 'var_2447');
INSERT INTO `turbine_model_points` VALUES (638, '20835', 0, 0, 0, 0, 'A30控制柜温度2（右边）太高故障', 'var_2448', 'B', 'notdefined', 'var_2448');
INSERT INTO `turbine_model_points` VALUES (639, '20835', 0, 0, 0, 0, 'A30控制柜温度2（右边）太低故障', 'var_2449', 'B', 'notdefined', 'var_2449');
INSERT INTO `turbine_model_points` VALUES (640, '20835', 0, 0, 0, 0, 'A30控制柜温度3（中间）高警告', 'var_2450', 'B', 'notdefined', 'var_2450');
INSERT INTO `turbine_model_points` VALUES (641, '20835', 0, 0, 0, 0, 'A30控制柜温度3（中间）低警告', 'var_2451', 'B', 'notdefined', 'var_2451');
INSERT INTO `turbine_model_points` VALUES (642, '20835', 0, 0, 0, 0, 'A30控制柜温度3（中间）太高故障', 'var_2452', 'B', 'notdefined', 'var_2452');
INSERT INTO `turbine_model_points` VALUES (643, '20835', 0, 0, 0, 0, 'A30控制柜温度3（中间）太低故障', 'var_2453', 'B', 'notdefined', 'var_2453');
INSERT INTO `turbine_model_points` VALUES (644, '20835', 0, 0, 0, 0, 'A11控制柜消防报警1级故障', 'var_2455', 'B', 'notdefined', 'var_2455');
INSERT INTO `turbine_model_points` VALUES (645, '20835', 0, 0, 0, 0, 'A30控制柜消防报警1级故障', 'var_2456', 'B', 'notdefined', 'var_2456');
INSERT INTO `turbine_model_points` VALUES (646, '20835', 0, 0, 0, 0, '电网模块1 CAN 通讯故障', 'var_2458', 'B', 'notdefined', 'var_2458');
INSERT INTO `turbine_model_points` VALUES (647, '20835', 0, 0, 0, 0, '电网模块2 CAN 通讯故障', 'var_2459', 'B', 'notdefined', 'var_2459');
INSERT INTO `turbine_model_points` VALUES (648, '20835', 0, 0, 0, 0, 'G-sensor 1 CAN 通讯故障', 'var_2460', 'B', 'notdefined', 'var_2460');
INSERT INTO `turbine_model_points` VALUES (649, '20835', 0, 0, 0, 0, 'G-sensor 2 CAN 通讯故障', 'var_2461', 'B', 'notdefined', 'var_2461');
INSERT INTO `turbine_model_points` VALUES (650, '20835', 0, 0, 0, 0, '变频器消防报警1级故障', 'var_2462', 'B', 'notdefined', 'var_2462');
INSERT INTO `turbine_model_points` VALUES (651, '20835', 0, 0, 0, 0, '箱变消防报警1级故障', 'var_2463', 'B', 'notdefined', 'var_2463');
INSERT INTO `turbine_model_points` VALUES (652, '20835', 0, 0, 0, 0, '轮毂烟雾探测器故障', 'var_2464', 'B', 'notdefined', 'var_2464');
INSERT INTO `turbine_model_points` VALUES (653, '20835', 0, 0, 0, 0, 'A30控制柜消防报警2级故障', 'var_2465', 'B', 'notdefined', 'var_2465');
INSERT INTO `turbine_model_points` VALUES (654, '20835', 0, 0, 0, 0, 'A11控制柜消防报警2级故障', 'var_2466', 'B', 'notdefined', 'var_2466');
INSERT INTO `turbine_model_points` VALUES (655, '20835', 0, 0, 0, 0, '变频器消防报警2级故障', 'var_2468', 'B', 'notdefined', 'var_2468');
INSERT INTO `turbine_model_points` VALUES (656, '20835', 0, 0, 0, 0, '箱变消防报警2级故障', 'var_2469', 'B', 'notdefined', 'var_2469');
INSERT INTO `turbine_model_points` VALUES (657, '20835', 0, 0, 0, 0, '风机停机维护故障', 'var_2470', 'B', 'notdefined', 'var_2470');
INSERT INTO `turbine_model_points` VALUES (658, '20835', 0, 0, 0, 0, '维护转子速度高故障', 'var_2471', 'B', 'notdefined', 'var_2471');
INSERT INTO `turbine_model_points` VALUES (659, '20835', 0, 0, 0, 0, '维护用户等级低', 'var_2472', 'B', 'notdefined', 'var_2472');
INSERT INTO `turbine_model_points` VALUES (660, '20835', 0, 0, 0, 0, '风速太高禁止维护警告', 'var_2473', 'B', 'notdefined', 'var_2473');
INSERT INTO `turbine_model_points` VALUES (661, '20835', 0, 0, 0, 0, '变桨维护激活故障', 'var_2474', 'B', 'notdefined', 'var_2474');
INSERT INTO `turbine_model_points` VALUES (662, '20835', 0, 0, 0, 0, '维护停机过程不成功故障', 'var_2475', 'B', 'notdefined', 'var_2475');
INSERT INTO `turbine_model_points` VALUES (663, '20835', 0, 0, 0, 0, '维护系统无效参数配置故障', 'var_2476', 'B', 'notdefined', 'var_2476');
INSERT INTO `turbine_model_points` VALUES (664, '20835', 0, 0, 0, 0, '盘车电机激活故障', 'var_2477', 'B', 'notdefined', 'var_2477');
INSERT INTO `turbine_model_points` VALUES (665, '20835', 0, 0, 0, 0, '环境温度低故障', 'var_2479', 'B', 'notdefined', 'var_2479');
INSERT INTO `turbine_model_points` VALUES (666, '20835', 0, 0, 0, 0, '1s平均风速高故障', 'var_2480', 'B', 'notdefined', 'var_2480');
INSERT INTO `turbine_model_points` VALUES (667, '20835', 0, 0, 0, 0, '30s平均风速高故障', 'var_2481', 'B', 'notdefined', 'var_2481');
INSERT INTO `turbine_model_points` VALUES (668, '20835', 0, 0, 0, 0, '600s平均风速高故障', 'var_2482', 'B', 'notdefined', 'var_2482');
INSERT INTO `turbine_model_points` VALUES (669, '20835', 0, 0, 0, 0, '自动模式气象站1警告', 'var_2485', 'B', 'notdefined', 'var_2485');
INSERT INTO `turbine_model_points` VALUES (670, '20835', 0, 0, 0, 0, '自动模式气象站2警告', 'var_2486', 'B', 'notdefined', 'var_2486');
INSERT INTO `turbine_model_points` VALUES (671, '20835', 0, 0, 0, 0, '风速在启动运行范围之外', 'var_2489', 'B', 'notdefined', 'var_2489');
INSERT INTO `turbine_model_points` VALUES (672, '20835', 0, 0, 0, 0, '手动选择气象站1警告', 'var_2490', 'B', 'notdefined', 'var_2490');
INSERT INTO `turbine_model_points` VALUES (673, '20835', 0, 0, 0, 0, '手动选择气象站2警告', 'var_2491', 'B', 'notdefined', 'var_2491');
INSERT INTO `turbine_model_points` VALUES (674, '20835', 0, 0, 0, 0, '600s平均风速太低故障', 'var_2492', 'B', 'notdefined', 'var_2492');
INSERT INTO `turbine_model_points` VALUES (675, '20835', 0, 0, 0, 0, '气象站无效配置故障', 'var_2493', 'B', 'notdefined', 'var_2493');
INSERT INTO `turbine_model_points` VALUES (676, '20835', 0, 0, 0, 0, '本地模式气象站3错误故障', 'var_2494', 'B', 'notdefined', 'var_2494');
INSERT INTO `turbine_model_points` VALUES (677, '20835', 0, 0, 0, 0, '远程模式气象站3错误故障', 'var_2495', 'B', 'notdefined', 'var_2495');
INSERT INTO `turbine_model_points` VALUES (678, '20835', 0, 0, 0, 0, '手动选择气象站3警告', 'var_2496', 'B', 'notdefined', 'var_2496');
INSERT INTO `turbine_model_points` VALUES (679, '20835', 0, 0, 0, 0, '转子刹车投入测试失败故障', 'var_2497', 'B', 'notdefined', 'var_2497');
INSERT INTO `turbine_model_points` VALUES (680, '20835', 0, 0, 0, 0, '风机启动故障', 'var_2500', 'B', 'notdefined', 'var_2500');
INSERT INTO `turbine_model_points` VALUES (681, '20835', 0, 0, 0, 0, '机组停机自检故障', 'var_2501', 'B', 'notdefined', 'var_2501');
INSERT INTO `turbine_model_points` VALUES (682, '20835', 0, 0, 0, 0, '停机过程不成功故障', 'var_2502', 'B', 'notdefined', 'var_2502');
INSERT INTO `turbine_model_points` VALUES (683, '20835', 0, 0, 0, 0, '停机空转刹车释放警告', 'var_2504', 'B', 'notdefined', 'var_2504');
INSERT INTO `turbine_model_points` VALUES (684, '20835', 0, 0, 0, 0, '变桨润滑条件OK故障', 'var_2506', 'B', 'notdefined', 'var_2506');
INSERT INTO `turbine_model_points` VALUES (685, '20835', 0, 0, 0, 0, '变桨润滑发电机超速报警故障', 'var_2507', 'B', 'notdefined', 'var_2507');
INSERT INTO `turbine_model_points` VALUES (686, '20835', 0, 0, 0, 0, '变桨润滑等待变桨移动故障', 'var_2508', 'B', 'notdefined', 'var_2508');
INSERT INTO `turbine_model_points` VALUES (687, '20835', 0, 0, 0, 0, '机舱温度低警告', 'var_2509', 'B', 'notdefined', 'var_2509');
INSERT INTO `turbine_model_points` VALUES (688, '20835', 0, 0, 0, 0, '机舱温度高警告', 'var_2510', 'B', 'notdefined', 'var_2510');
INSERT INTO `turbine_model_points` VALUES (689, '20835', 0, 0, 0, 0, '机舱冷却空气压差反馈1警告', 'var_2517', 'B', 'notdefined', 'var_2517');
INSERT INTO `turbine_model_points` VALUES (690, '20835', 0, 0, 0, 0, '机舱湿度高故障', 'var_2519', 'B', 'notdefined', 'var_2519');
INSERT INTO `turbine_model_points` VALUES (691, '20835', 0, 0, 0, 0, '机舱湿度高警告', 'var_2520', 'B', 'notdefined', 'var_2520');
INSERT INTO `turbine_model_points` VALUES (692, '20835', 0, 0, 0, 0, '机舱外部冷却风扇1过载故障', 'var_2521', 'B', 'notdefined', 'var_2521');
INSERT INTO `turbine_model_points` VALUES (693, '20835', 0, 0, 0, 0, '机舱外部冷却风扇2过载故障', 'var_2522', 'B', 'notdefined', 'var_2522');
INSERT INTO `turbine_model_points` VALUES (694, '20835', 0, 0, 0, 0, '机舱外部冷却空气压差1反馈警告', 'var_2523', 'B', 'notdefined', 'var_2523');
INSERT INTO `turbine_model_points` VALUES (695, '20835', 0, 0, 0, 0, '机舱冷却风扇1过载警告', 'var_2525', 'B', 'notdefined', 'var_2525');
INSERT INTO `turbine_model_points` VALUES (696, '20835', 0, 0, 0, 0, '机舱冷却风扇2过载警告', 'var_2526', 'B', 'notdefined', 'var_2526');
INSERT INTO `turbine_model_points` VALUES (697, '20835', 0, 0, 0, 0, '机舱冷却风扇过载故障', 'var_2527', 'B', 'notdefined', 'var_2527');
INSERT INTO `turbine_model_points` VALUES (698, '20835', 0, 0, 0, 0, '机舱除湿机过载警告', 'var_2528', 'B', 'notdefined', 'var_2528');
INSERT INTO `turbine_model_points` VALUES (699, '20835', 0, 0, 0, 0, '机舱除湿机故障警告', 'var_2529', 'B', 'notdefined', 'var_2529');
INSERT INTO `turbine_model_points` VALUES (700, '20835', 0, 0, 0, 0, '机舱水泵1过载警告', 'var_2530', 'B', 'notdefined', 'var_2530');
INSERT INTO `turbine_model_points` VALUES (701, '20835', 0, 0, 0, 0, '机舱水泵2过载警告', 'var_2531', 'B', 'notdefined', 'var_2531');
INSERT INTO `turbine_model_points` VALUES (702, '20835', 0, 0, 0, 0, '航空灯过载警告', 'var_2532', 'B', 'notdefined', 'var_2532');
INSERT INTO `turbine_model_points` VALUES (703, '20835', 0, 0, 0, 0, '空气交换系统过载警告', 'var_2535', 'B', 'notdefined', 'var_2535');
INSERT INTO `turbine_model_points` VALUES (704, '20835', 0, 0, 0, 0, '电网1监视L1相欠压故障', 'var_2536', 'B', 'notdefined', 'var_2536');
INSERT INTO `turbine_model_points` VALUES (705, '20835', 0, 0, 0, 0, '电网1监视L1相过压故障', 'var_2537', 'B', 'notdefined', 'var_2537');
INSERT INTO `turbine_model_points` VALUES (706, '20835', 0, 0, 0, 0, '电网1监视L2相欠压故障', 'var_2538', 'B', 'notdefined', 'var_2538');
INSERT INTO `turbine_model_points` VALUES (707, '20835', 0, 0, 0, 0, '电网1监视L2相过压故障', 'var_2539', 'B', 'notdefined', 'var_2539');
INSERT INTO `turbine_model_points` VALUES (708, '20835', 0, 0, 0, 0, '电网1监视L3相欠压故障', 'var_2540', 'B', 'notdefined', 'var_2540');
INSERT INTO `turbine_model_points` VALUES (709, '20835', 0, 0, 0, 0, '电网1监视L3相过压故障', 'var_2541', 'B', 'notdefined', 'var_2541');
INSERT INTO `turbine_model_points` VALUES (710, '20835', 0, 0, 0, 0, '电网1监视L1相过流故障', 'var_2542', 'B', 'notdefined', 'var_2542');
INSERT INTO `turbine_model_points` VALUES (711, '20835', 0, 0, 0, 0, '电网1监视L2相过流故障', 'var_2543', 'B', 'notdefined', 'var_2543');
INSERT INTO `turbine_model_points` VALUES (712, '20835', 0, 0, 0, 0, '电网1监视L3相过流故障', 'var_2544', 'B', 'notdefined', 'var_2544');
INSERT INTO `turbine_model_points` VALUES (713, '20835', 0, 0, 0, 0, '电网1监视电网1频率低故障', 'var_2545', 'B', 'notdefined', 'var_2545');
INSERT INTO `turbine_model_points` VALUES (714, '20835', 0, 0, 0, 0, '电网1监视电网1频率高故障', 'var_2546', 'B', 'notdefined', 'var_2546');
INSERT INTO `turbine_model_points` VALUES (715, '20835', 0, 0, 0, 0, '电网1监视电压不平衡故障', 'var_2547', 'B', 'notdefined', 'var_2547');
INSERT INTO `turbine_model_points` VALUES (716, '20835', 0, 0, 0, 0, '电网1监视相间电流差过大故障', 'var_2548', 'B', 'notdefined', 'var_2548');
INSERT INTO `turbine_model_points` VALUES (717, '20835', 0, 0, 0, 0, '电网1监视电网1正常电流相差太高故障', 'var_2549', 'B', 'notdefined', 'var_2549');
INSERT INTO `turbine_model_points` VALUES (718, '20835', 0, 0, 0, 0, '电网1监视电网1相序错误故障', 'var_2550', 'B', 'notdefined', 'var_2550');
INSERT INTO `turbine_model_points` VALUES (719, '20835', 0, 0, 0, 0, '电网2监视L1相欠压故障', 'var_2551', 'B', 'notdefined', 'var_2551');
INSERT INTO `turbine_model_points` VALUES (720, '20835', 0, 0, 0, 0, '电网2监视L1相过压故障', 'var_2552', 'B', 'notdefined', 'var_2552');
INSERT INTO `turbine_model_points` VALUES (721, '20835', 0, 0, 0, 0, '电网2监视L2相欠压故障', 'var_2553', 'B', 'notdefined', 'var_2553');
INSERT INTO `turbine_model_points` VALUES (722, '20835', 0, 0, 0, 0, '电网2监视L2相过压故障', 'var_2554', 'B', 'notdefined', 'var_2554');
INSERT INTO `turbine_model_points` VALUES (723, '20835', 0, 0, 0, 0, '电网2监视L3相欠压故障', 'var_2555', 'B', 'notdefined', 'var_2555');
INSERT INTO `turbine_model_points` VALUES (724, '20835', 0, 0, 0, 0, '电网2监视L3相过压故障', 'var_2556', 'B', 'notdefined', 'var_2556');
INSERT INTO `turbine_model_points` VALUES (725, '20835', 0, 0, 0, 0, '电网2监视L1相过流故障', 'var_2557', 'B', 'notdefined', 'var_2557');
INSERT INTO `turbine_model_points` VALUES (726, '20835', 0, 0, 0, 0, '电网2监视L2相过流故障', 'var_2558', 'B', 'notdefined', 'var_2558');
INSERT INTO `turbine_model_points` VALUES (727, '20835', 0, 0, 0, 0, '电网2监视L3相过流故障', 'var_2559', 'B', 'notdefined', 'var_2559');
INSERT INTO `turbine_model_points` VALUES (728, '20835', 0, 0, 0, 0, '电网2监视电网2频率低故障', 'var_2560', 'B', 'notdefined', 'var_2560');
INSERT INTO `turbine_model_points` VALUES (729, '20835', 0, 0, 0, 0, '电网2监视电网2频率高故障', 'var_2561', 'B', 'notdefined', 'var_2561');
INSERT INTO `turbine_model_points` VALUES (730, '20835', 0, 0, 0, 0, '电网2监视电压不平衡故障', 'var_2562', 'B', 'notdefined', 'var_2562');
INSERT INTO `turbine_model_points` VALUES (731, '20835', 0, 0, 0, 0, '电网2监视相间电流差过大故障', 'var_2563', 'B', 'notdefined', 'var_2563');
INSERT INTO `turbine_model_points` VALUES (732, '20835', 0, 0, 0, 0, '电网2监视电网2正常电流相差太高故障', 'var_2564', 'B', 'notdefined', 'var_2564');
INSERT INTO `turbine_model_points` VALUES (733, '20835', 0, 0, 0, 0, '电网2监视电网2相序错误故障', 'var_2565', 'B', 'notdefined', 'var_2565');
INSERT INTO `turbine_model_points` VALUES (734, '20835', 0, 0, 0, 0, '电网1监控电网1的L1相严重过压故障', 'var_2566', 'B', 'notdefined', 'var_2566');
INSERT INTO `turbine_model_points` VALUES (735, '20835', 0, 0, 0, 0, '电网1监控电网1的L2相严重过压故障', 'var_2567', 'B', 'notdefined', 'var_2567');
INSERT INTO `turbine_model_points` VALUES (736, '20835', 0, 0, 0, 0, '电网1监控电网1的L3相严重过压故障', 'var_2568', 'B', 'notdefined', 'var_2568');
INSERT INTO `turbine_model_points` VALUES (737, '20835', 0, 0, 0, 0, '电网2监控电网2的L1相严重过压故障', 'var_2569', 'B', 'notdefined', 'var_2569');
INSERT INTO `turbine_model_points` VALUES (738, '20835', 0, 0, 0, 0, '电网2监控电网2的L2相严重过压故障', 'var_2570', 'B', 'notdefined', 'var_2570');
INSERT INTO `turbine_model_points` VALUES (739, '20835', 0, 0, 0, 0, '电网2监控电网2的L3相严重过压故障', 'var_2571', 'B', 'notdefined', 'var_2571');
INSERT INTO `turbine_model_points` VALUES (740, '20835', 0, 0, 0, 0, '电网监控无效配置故障', 'var_2572', 'B', 'notdefined', 'var_2572');
INSERT INTO `turbine_model_points` VALUES (741, '20835', 0, 0, 0, 0, '电网1监控辅助电源L1相过压故障', 'var_2573', 'B', 'notdefined', 'var_2573');
INSERT INTO `turbine_model_points` VALUES (742, '20835', 0, 0, 0, 0, '电网1监控辅助电源L2相过压故障', 'var_2574', 'B', 'notdefined', 'var_2574');
INSERT INTO `turbine_model_points` VALUES (743, '20835', 0, 0, 0, 0, '电网1监控辅助电源L3相过压故障', 'var_2575', 'B', 'notdefined', 'var_2575');
INSERT INTO `turbine_model_points` VALUES (744, '20835', 0, 0, 0, 0, '电网2监控辅助电源L1相过压故障', 'var_2576', 'B', 'notdefined', 'var_2576');
INSERT INTO `turbine_model_points` VALUES (745, '20835', 0, 0, 0, 0, '电网2监控辅助电源L2相过压故障', 'var_2577', 'B', 'notdefined', 'var_2577');
INSERT INTO `turbine_model_points` VALUES (746, '20835', 0, 0, 0, 0, '电网2监控辅助电源L3相过压故障', 'var_2578', 'B', 'notdefined', 'var_2578');
INSERT INTO `turbine_model_points` VALUES (747, '20835', 0, 0, 0, 0, '功率速度控制器SVI通讯连接故障', 'var_2579', 'B', 'notdefined', 'var_2579');
INSERT INTO `turbine_model_points` VALUES (748, '20835', 0, 0, 0, 0, '功率速度控制器SVI通讯地址故障', 'var_2580', 'B', 'notdefined', 'var_2580');
INSERT INTO `turbine_model_points` VALUES (749, '20835', 0, 0, 0, 0, '功率速度控制器SVI通讯故障', 'var_2581', 'B', 'notdefined', 'var_2581');
INSERT INTO `turbine_model_points` VALUES (750, '20835', 0, 0, 0, 0, '停机进行变桨系统润滑故障', 'var_2582', 'B', 'notdefined', 'var_2582');
INSERT INTO `turbine_model_points` VALUES (751, '20835', 0, 0, 0, 0, '功率速度控制器转矩参考波动超限故障', 'var_2583', 'B', 'notdefined', 'var_2583');
INSERT INTO `turbine_model_points` VALUES (752, '20835', 0, 0, 0, 0, '功率速度控制器滤波器参数设置无效警告', 'var_2584', 'B', 'notdefined', 'var_2584');
INSERT INTO `turbine_model_points` VALUES (753, '20835', 0, 0, 0, 0, '功率速度控制器参数配置无效故障', 'var_2585', 'B', 'notdefined', 'var_2585');
INSERT INTO `turbine_model_points` VALUES (754, '20835', 0, 0, 0, 0, '功率速度控制SVI成员超限故障', 'var_2586', 'B', 'notdefined', 'var_2586');
INSERT INTO `turbine_model_points` VALUES (755, '20835', 0, 0, 0, 0, '塔基温度低警告', 'var_2587', 'B', 'notdefined', 'var_2587');
INSERT INTO `turbine_model_points` VALUES (756, '20835', 0, 0, 0, 0, '塔基温度高警告', 'var_2588', 'B', 'notdefined', 'var_2588');
INSERT INTO `turbine_model_points` VALUES (757, '20835', 0, 0, 0, 0, '塔基温度低故障', 'var_2589', 'B', 'notdefined', 'var_2589');
INSERT INTO `turbine_model_points` VALUES (758, '20835', 0, 0, 0, 0, '塔基温度高故障', 'var_2590', 'B', 'notdefined', 'var_2590');
INSERT INTO `turbine_model_points` VALUES (759, '20835', 0, 0, 0, 0, '塔基冷却风扇1-2过载警告', 'var_2591', 'B', 'notdefined', 'var_2591');
INSERT INTO `turbine_model_points` VALUES (760, '20835', 0, 0, 0, 0, '塔基系统无效配置故障', 'var_2593', 'B', 'notdefined', 'var_2593');
INSERT INTO `turbine_model_points` VALUES (761, '20835', 0, 0, 0, 0, '塔基湿度高警告', 'var_2594', 'B', 'notdefined', 'var_2594');
INSERT INTO `turbine_model_points` VALUES (762, '20835', 0, 0, 0, 0, '塔基湿度过高故障', 'var_2595', 'B', 'notdefined', 'var_2595');
INSERT INTO `turbine_model_points` VALUES (763, '20835', 0, 0, 0, 0, '塔基除湿机故障警告', 'var_2596', 'B', 'notdefined', 'var_2596');
INSERT INTO `turbine_model_points` VALUES (764, '20835', 0, 0, 0, 0, '航海障碍灯过载警告', 'var_2597', 'B', 'notdefined', 'var_2597');
INSERT INTO `turbine_model_points` VALUES (765, '20835', 0, 0, 0, 0, '塔基功率电缆温度过高警告', 'var_2598', 'B', 'notdefined', 'var_2598');
INSERT INTO `turbine_model_points` VALUES (766, '20835', 0, 0, 0, 0, '塔基休息间风扇过载警告', 'var_2599', 'B', 'notdefined', 'var_2599');
INSERT INTO `turbine_model_points` VALUES (767, '20835', 0, 0, 0, 0, '塔基换气系统过载警告', 'var_2600', 'B', 'notdefined', 'var_2600');
INSERT INTO `turbine_model_points` VALUES (768, '20835', 0, 0, 0, 0, '变频器消防系统压力低警告', 'var_2601', 'B', 'notdefined', 'var_2601');
INSERT INTO `turbine_model_points` VALUES (769, '20835', 0, 0, 0, 0, '机舱消防系统压力低警告', 'var_2602', 'B', 'notdefined', 'var_2602');
INSERT INTO `turbine_model_points` VALUES (770, '20835', 0, 0, 0, 0, '箱变消防系统压力低警告', 'var_2603', 'B', 'notdefined', 'var_2603');
INSERT INTO `turbine_model_points` VALUES (771, '20835', 0, 0, 0, 0, '塔基消防系统压力低警告', 'var_2604', 'B', 'notdefined', 'var_2604');
INSERT INTO `turbine_model_points` VALUES (772, '20835', 0, 0, 0, 0, 'IPC系统通讯错误故障', 'var_2605', 'B', 'notdefined', 'var_2605');
INSERT INTO `turbine_model_points` VALUES (773, '20835', 0, 0, 0, 0, 'IPC通讯重新初始化故障', 'var_2606', 'B', 'notdefined', 'var_2606');
INSERT INTO `turbine_model_points` VALUES (774, '20835', 0, 0, 0, 0, 'IPC的SVI通讯错误故障', 'var_2607', 'B', 'notdefined', 'var_2607');
INSERT INTO `turbine_model_points` VALUES (775, '20835', 0, 0, 0, 0, 'IPC无效滤波器参数设置错误警告', 'var_2608', 'B', 'notdefined', 'var_2608');
INSERT INTO `turbine_model_points` VALUES (776, '20835', 0, 0, 0, 0, 'IPC无效参数配置故障', 'var_2609', 'B', 'notdefined', 'var_2609');
INSERT INTO `turbine_model_points` VALUES (777, '20835', 0, 0, 0, 0, 'IPC的SVI通讯连接错误故障', 'var_2610', 'B', 'notdefined', 'var_2610');
INSERT INTO `turbine_model_points` VALUES (778, '20835', 0, 0, 0, 0, 'IPC的SVI通讯地址错误故障', 'var_2611', 'B', 'notdefined', 'var_2611');
INSERT INTO `turbine_model_points` VALUES (779, '20835', 0, 0, 0, 0, 'IPC的SVI成员超限故障', 'var_2612', 'B', 'notdefined', 'var_2612');
INSERT INTO `turbine_model_points` VALUES (780, '20835', 0, 0, 0, 0, '齿轮箱油旁路过滤器压差太高警告', 'var_2632', 'B', 'notdefined', 'var_2632');
INSERT INTO `turbine_model_points` VALUES (781, '20835', 1, 1, 0, 0, '发电机冷却风扇2', 'var_2635', 'B', 'notdefined', 'var_2635');
INSERT INTO `turbine_model_points` VALUES (782, '20835', 0, 0, 0, 0, '变频器冷却泵1加热器', 'var_2638', 'B', 'notdefined', 'var_2638');
INSERT INTO `turbine_model_points` VALUES (783, '20835', 1, 1, 0, 0, '变频器冷却泵1电机', 'var_2639', 'B', 'notdefined', 'var_2639');
INSERT INTO `turbine_model_points` VALUES (784, '20835', 1, 1, 0, 0, '变频器冷却风扇1高速', 'var_2640', 'B', 'notdefined', 'var_2640');
INSERT INTO `turbine_model_points` VALUES (785, '20835', 1, 1, 0, 0, '变频器冷却风扇1低速', 'var_2641', 'B', 'notdefined', 'var_2641');
INSERT INTO `turbine_model_points` VALUES (786, '20835', 0, 0, 0, 0, '变频器冷却泵2加热器', 'var_2642', 'B', 'notdefined', 'var_2642');
INSERT INTO `turbine_model_points` VALUES (787, '20835', 1, 1, 0, 0, '变频器冷却泵2电机', 'var_2643', 'B', 'notdefined', 'var_2643');
INSERT INTO `turbine_model_points` VALUES (788, '20835', 1, 1, 0, 0, '变频器冷却风扇2高速', 'var_2644', 'B', 'notdefined', 'var_2644');
INSERT INTO `turbine_model_points` VALUES (789, '20835', 1, 1, 0, 0, '变频器冷却风扇2低速', 'var_2645', 'B', 'notdefined', 'var_2645');
INSERT INTO `turbine_model_points` VALUES (790, '20835', 0, 0, 0, 0, '变频器冷却泵3加热器', 'var_2646', 'B', 'notdefined', 'var_2646');
INSERT INTO `turbine_model_points` VALUES (791, '20835', 1, 1, 0, 0, '变频器冷却泵3电机', 'var_2647', 'B', 'notdefined', 'var_2647');
INSERT INTO `turbine_model_points` VALUES (792, '20835', 1, 1, 0, 0, '变频器冷却风扇3高速', 'var_2648', 'B', 'notdefined', 'var_2648');
INSERT INTO `turbine_model_points` VALUES (793, '20835', 1, 1, 0, 0, '变频器冷却风扇3低速', 'var_2649', 'B', 'notdefined', 'var_2649');
INSERT INTO `turbine_model_points` VALUES (794, '20835', 0, 0, 0, 0, '变频器冷却泵4加热器', 'var_2650', 'B', 'notdefined', 'var_2650');
INSERT INTO `turbine_model_points` VALUES (795, '20835', 1, 1, 0, 0, '变频器冷却泵4电机', 'var_2651', 'B', 'notdefined', 'var_2651');
INSERT INTO `turbine_model_points` VALUES (796, '20835', 1, 1, 0, 0, '变频器冷却风扇4高速', 'var_2652', 'B', 'notdefined', 'var_2652');
INSERT INTO `turbine_model_points` VALUES (797, '20835', 1, 1, 0, 0, '变频器冷却风扇4低速', 'var_2653', 'B', 'notdefined', 'var_2653');
INSERT INTO `turbine_model_points` VALUES (798, '20835', 0, 0, 0, 0, '变桨轴承润滑时间未达标警告', 'var_2654', 'B', 'notdefined', 'var_2654');
INSERT INTO `turbine_model_points` VALUES (799, '20835', 0, 0, 0, 0, '变桨轴齿轮滑时间未达标警告', 'var_2655', 'B', 'notdefined', 'var_2655');
INSERT INTO `turbine_model_points` VALUES (800, '20835', 0, 0, 0, 0, '变桨轴滑时间未达标故障', 'var_2656', 'B', 'notdefined', 'var_2656');
INSERT INTO `turbine_model_points` VALUES (801, '20835', 0, 0, 0, 0, '主轴承润滑泵', 'var_2657', 'B', 'notdefined', 'var_2657');
INSERT INTO `turbine_model_points` VALUES (802, '20835', 0, 0, 0, 0, '偏航逆时针旋转极限开关激活', 'var_2660', 'B', 'notdefined', 'var_2660');
INSERT INTO `turbine_model_points` VALUES (803, '20835', 0, 0, 0, 0, '偏航顺时针旋转极限开关激活', 'var_2661', 'B', 'notdefined', 'var_2661');
INSERT INTO `turbine_model_points` VALUES (804, '20835', 0, 0, 0, 0, '液压油泵电机1', 'var_2662', 'B', 'notdefined', 'var_2662');
INSERT INTO `turbine_model_points` VALUES (805, '20835', 0, 0, 0, 0, '机舱外部冷却风扇1过载警告1', 'var_2666', 'B', 'notdefined', 'var_2666');
INSERT INTO `turbine_model_points` VALUES (806, '20835', 0, 0, 0, 0, '机舱外部冷却风扇2过载警告1', 'var_2667', 'B', 'notdefined', 'var_2667');
INSERT INTO `turbine_model_points` VALUES (807, '20835', 0, 0, 0, 0, '偏航电机刹车微动开关反馈故障', 'var_2668', 'B', 'notdefined', 'var_2668');
INSERT INTO `turbine_model_points` VALUES (808, '20835', 0, 0, 0, 0, '2#风速仪10min平均风速', 'var_2707', 'F', 'm/s', 'var_2707');
INSERT INTO `turbine_model_points` VALUES (809, '20835', 0, 0, 0, 0, '2#风速仪10s平均风速', 'var_2706', 'F', 'm/s', 'var_2706');
INSERT INTO `turbine_model_points` VALUES (810, '20835', 0, 0, 0, 0, '1#风速仪10min平均风速', 'var_2705', 'F', 'm/s', 'var_2705');
INSERT INTO `turbine_model_points` VALUES (811, '20835', 0, 0, 0, 0, '1#风速仪10s平均风速', 'var_2704', 'F', 'm/s', 'var_2704');
INSERT INTO `turbine_model_points` VALUES (812, '20835', 0, 0, 0, 0, '10s平均风向', 'var_2708', 'F', '°', 'var_2708');
INSERT INTO `turbine_model_points` VALUES (813, '20835', 0, 0, 0, 0, '2#风向仪10min平均风向', 'var_2703', 'F', '°', 'var_2703');
INSERT INTO `turbine_model_points` VALUES (814, '20835', 0, 0, 0, 0, '2#风向仪10s平均风向 ', 'var_2702', 'F', '°', 'var_2702');
INSERT INTO `turbine_model_points` VALUES (815, '20835', 0, 0, 0, 0, '1#风向仪10min平均风向', 'var_2701', 'F', '°', 'var_2701');
INSERT INTO `turbine_model_points` VALUES (816, '20835', 0, 0, 0, 0, '1#风向仪10s平均风向 ', 'var_2700', 'F', '°', 'var_2700');
INSERT INTO `turbine_model_points` VALUES (817, '20835', 1, 0, 0, 0, '塔基湿度', 'var_2699', 'F', '%', 'var_2699');
INSERT INTO `turbine_model_points` VALUES (818, '20835', 0, 0, 0, 0, '辅助变压器绕组温度', 'var_2697', 'F', '°C', 'var_2697');
INSERT INTO `turbine_model_points` VALUES (819, '20835', 0, 0, 0, 0, '塔基电缆温度', 'var_2696', 'F', '°C', 'var_2696');
INSERT INTO `turbine_model_points` VALUES (820, '20835', 0, 0, 0, 0, '机组视在总损耗电量', 'var_2695', 'F', 'kVArh', 'var_2695');
INSERT INTO `turbine_model_points` VALUES (821, '20835', 0, 0, 0, 0, '气象站加热状态', 'var_2718', 'I', 'notdefined', 'var_2718');
INSERT INTO `turbine_model_points` VALUES (822, '20835', 0, 0, 0, 0, '气象站状态', 'var_2719', 'I', 'notdefined', 'var_2719');
INSERT INTO `turbine_model_points` VALUES (823, '20835', 0, 0, 0, 0, '阻尼偏航压力值过高故障', 'var_2765', 'B', 'notdefined', 'var_2765');
INSERT INTO `turbine_model_points` VALUES (824, '20835', 0, 0, 0, 0, '偏航解缆压力过高故障', 'var_2766', 'B', 'notdefined', 'var_2766');
INSERT INTO `turbine_model_points` VALUES (825, '20835', 0, 0, 0, 0, '1#液压站压力过高故障', 'var_2767', 'B', 'notdefined', 'var_2767');
INSERT INTO `turbine_model_points` VALUES (826, '20835', 0, 0, 0, 0, '变桨停机润滑故障', 'var_2773', 'B', 'notdefined', 'var_2773');
INSERT INTO `turbine_model_points` VALUES (827, '20835', 0, 0, 0, 0, '齿轮箱油泵电机待机加热过载警告', 'var_2774', 'B', 'notdefined', 'var_2774');
INSERT INTO `turbine_model_points` VALUES (828, '20835', 0, 0, 0, 0, '齿轮箱旁路过滤电机过载警告', 'var_2775', 'B', 'notdefined', 'var_2775');
INSERT INTO `turbine_model_points` VALUES (829, '20835', 0, 0, 0, 0, '齿轮箱油泵电机1过载警告', 'var_2776', 'B', 'notdefined', 'var_2776');
INSERT INTO `turbine_model_points` VALUES (830, '20835', 0, 0, 0, 0, '齿轮箱油泵电机2过载警告', 'var_2777', 'B', 'notdefined', 'var_2777');
INSERT INTO `turbine_model_points` VALUES (831, '20835', 0, 0, 0, 0, '1#叶片编码器偏差过大警告', 'var_2778', 'B', 'notdefined', 'var_2778');
INSERT INTO `turbine_model_points` VALUES (832, '20835', 0, 0, 0, 0, '2#叶片编码器偏差过大警告', 'var_2779', 'B', 'notdefined', 'var_2779');
INSERT INTO `turbine_model_points` VALUES (833, '20835', 0, 0, 0, 0, '3#叶片编码器偏差过大警告', 'var_2780', 'B', 'notdefined', 'var_2780');
INSERT INTO `turbine_model_points` VALUES (834, '20835', 0, 0, 0, 0, '发电机润滑警告', 'var_2782', 'B', 'notdefined', 'var_2782');
INSERT INTO `turbine_model_points` VALUES (835, '20835', 0, 0, 0, 0, '发电机加热器过载警告', 'var_2783', 'B', 'notdefined', 'var_2783');
INSERT INTO `turbine_model_points` VALUES (836, '20835', 0, 0, 0, 0, '发电机电机加热器过载警告', 'var_2785', 'B', 'notdefined', 'var_2785');
INSERT INTO `turbine_model_points` VALUES (837, '20835', 0, 0, 0, 0, '发电机内部冷却风扇1过载警告', 'var_2786', 'B', 'notdefined', 'var_2786');
INSERT INTO `turbine_model_points` VALUES (838, '20835', 0, 0, 0, 0, '发电机内部冷却风扇2过载警告', 'var_2787', 'B', 'notdefined', 'var_2787');
INSERT INTO `turbine_model_points` VALUES (839, '20835', 0, 0, 0, 0, 'UPS电池容量低警告', 'var_2788', 'B', 'notdefined', 'var_2788');
INSERT INTO `turbine_model_points` VALUES (840, '20835', 0, 0, 0, 0, 'UPS旁路警告', 'var_2789', 'B', 'notdefined', 'var_2789');
INSERT INTO `turbine_model_points` VALUES (841, '20835', 0, 0, 0, 0, '箱变冷却风扇过载警告', 'var_2790', 'B', 'notdefined', 'var_2790');
INSERT INTO `turbine_model_points` VALUES (842, '20835', 0, 0, 0, 0, '箱变冷去风扇备用加热器过载警告', 'var_2791', 'B', 'notdefined', 'var_2791');
INSERT INTO `turbine_model_points` VALUES (843, '20835', 0, 0, 0, 0, '变频器1加热过载警告', 'var_2792', 'B', 'notdefined', 'var_2792');
INSERT INTO `turbine_model_points` VALUES (844, '20835', 0, 0, 0, 0, '变频器1未准备好加热要求警告', 'var_2793', 'B', 'notdefined', 'var_2793');
INSERT INTO `turbine_model_points` VALUES (845, '20835', 0, 0, 0, 0, '变频器2加热过载警告', 'var_2794', 'B', 'notdefined', 'var_2794');
INSERT INTO `turbine_model_points` VALUES (846, '20835', 0, 0, 0, 0, '变频器2未准备好加热要求警告', 'var_2795', 'B', 'notdefined', 'var_2795');
INSERT INTO `turbine_model_points` VALUES (847, '20835', 0, 0, 0, 0, '变频器3加热过载警告', 'var_2796', 'B', 'notdefined', 'var_2796');
INSERT INTO `turbine_model_points` VALUES (848, '20835', 0, 0, 0, 0, '变频器4加热过载警告', 'var_2797', 'B', 'notdefined', 'var_2797');
INSERT INTO `turbine_model_points` VALUES (849, '20835', 0, 0, 0, 0, '液压系统油位1低警告', 'var_2798', 'B', 'notdefined', 'var_2798');
INSERT INTO `turbine_model_points` VALUES (850, '20835', 0, 0, 0, 0, '液压系统液压泵1运行超时警告', 'var_2800', 'B', 'notdefined', 'var_2800');
INSERT INTO `turbine_model_points` VALUES (851, '20835', 0, 0, 0, 0, '速度传感器警告（安全控制器）', 'var_2802', 'B', 'notdefined', 'var_2802');
INSERT INTO `turbine_model_points` VALUES (852, '20835', 0, 0, 0, 0, '转子刹车1应用状态时压力太低警告', 'var_2803', 'B', 'notdefined', 'var_2803');
INSERT INTO `turbine_model_points` VALUES (853, '20835', 0, 0, 0, 0, '机舱冷却风扇过载警告', 'var_2810', 'B', 'notdefined', 'var_2810');
INSERT INTO `turbine_model_points` VALUES (854, '20835', 0, 0, 0, 0, '偏航条件解缆激活停机', 'var_2811', 'B', 'notdefined', 'var_2811');
INSERT INTO `turbine_model_points` VALUES (855, '20835', 0, 0, 0, 0, '偏航无条件解缆激活停机', 'var_2812', 'B', 'notdefined', 'var_2812');
INSERT INTO `turbine_model_points` VALUES (856, '20835', 0, 0, 0, 0, '偏航系统参数配置无效停机', 'var_2813', 'B', 'notdefined', 'var_2813');
INSERT INTO `turbine_model_points` VALUES (857, '20835', 0, 0, 0, 0, '超大风偏航策略激活停机', 'var_2814', 'B', 'notdefined', 'var_2814');
INSERT INTO `turbine_model_points` VALUES (858, '20835', 0, 0, 0, 0, '变桨系统报出1#叶片手动操作激活停机', 'var_2815', 'B', 'notdefined', 'var_2815');
INSERT INTO `turbine_model_points` VALUES (859, '20835', 0, 0, 0, 0, '距上次变桨轴承润滑时间太长停机', 'var_2817', 'B', 'notdefined', 'var_2817');
INSERT INTO `turbine_model_points` VALUES (860, '20835', 0, 0, 0, 0, '距上次变桨齿圈润滑时间太长停机', 'var_2818', 'B', 'notdefined', 'var_2818');
INSERT INTO `turbine_model_points` VALUES (861, '20835', 0, 0, 0, 0, '距上次变桨主轴润滑时间太长停机', 'var_2819', 'B', 'notdefined', 'var_2819');
INSERT INTO `turbine_model_points` VALUES (862, '20835', 0, 0, 0, 0, 'UPS关断停机', 'var_2820', 'B', 'notdefined', 'var_2820');
INSERT INTO `turbine_model_points` VALUES (863, '20835', 0, 0, 0, 0, '本地手动停机消息', 'var_2822', 'B', 'notdefined', 'var_2822');
INSERT INTO `turbine_model_points` VALUES (864, '20835', 0, 0, 0, 0, 'SCADA远程断开C1柜停机', 'var_2823', 'B', 'notdefined', 'var_2823');
INSERT INTO `turbine_model_points` VALUES (865, '20835', 0, 0, 0, 0, 'SCADA远程断开C2柜停机', 'var_2824', 'B', 'notdefined', 'var_2824');
INSERT INTO `turbine_model_points` VALUES (866, '20835', 0, 0, 0, 0, 'SCADA远程断开V柜停机', 'var_2825', 'B', 'notdefined', 'var_2825');
INSERT INTO `turbine_model_points` VALUES (867, '20835', 0, 0, 0, 0, '发电机机械速度太低停机', 'var_2826', 'B', 'notdefined', 'var_2826');
INSERT INTO `turbine_model_points` VALUES (868, '20835', 0, 0, 0, 0, '风机停机维护停机', 'var_2827', 'B', 'notdefined', 'var_2827');
INSERT INTO `turbine_model_points` VALUES (869, '20835', 0, 0, 0, 0, '维护转子速度高停机', 'var_2828', 'B', 'notdefined', 'var_2828');
INSERT INTO `turbine_model_points` VALUES (870, '20835', 0, 0, 0, 0, '维护用户等级过低停机', 'var_2829', 'B', 'notdefined', 'var_2829');
INSERT INTO `turbine_model_points` VALUES (871, '20835', 0, 0, 0, 0, '变桨维护激活停机', 'var_2830', 'B', 'notdefined', 'var_2830');
INSERT INTO `turbine_model_points` VALUES (872, '20835', 0, 0, 0, 0, '维护停机过程不成功停机', 'var_2831', 'B', 'notdefined', 'var_2831');
INSERT INTO `turbine_model_points` VALUES (873, '20835', 0, 0, 0, 0, '发电机冷却空气出口温度', 'var_2763', 'F', '°C', 'var_2763');
INSERT INTO `turbine_model_points` VALUES (874, '20835', 0, 0, 0, 0, '发电机冷却空气进口温度2', 'var_2762', 'F', '°C', 'var_2762');
INSERT INTO `turbine_model_points` VALUES (875, '20835', 0, 0, 0, 0, '发电机冷却空气进口温度1', 'var_2761', 'F', '°C', 'var_2761');
INSERT INTO `turbine_model_points` VALUES (876, '20835', 0, 0, 0, 0, '变频器出口有功功率', 'var_2759', 'F', 'kW', 'var_2759');
INSERT INTO `turbine_model_points` VALUES (877, '20835', 1, 0, 0, 0, '齿轮箱过滤器3压差', 'var_2715', 'F', 'Bar', 'var_2715');
INSERT INTO `turbine_model_points` VALUES (878, '20835', 1, 0, 0, 0, '齿轮箱过滤器2压差', 'var_2714', 'F', 'Bar', 'var_2714');
INSERT INTO `turbine_model_points` VALUES (879, '20835', 1, 0, 0, 0, '齿轮箱过滤器1压差', 'var_2713', 'F', 'Bar', 'var_2713');
INSERT INTO `turbine_model_points` VALUES (880, '20835', 0, 0, 0, 0, '60s平均风向', 'var_2711', 'F', '°', 'var_2711');
INSERT INTO `turbine_model_points` VALUES (881, '20835', 0, 0, 0, 0, '180s平均风向', 'var_2710', 'F', '°', 'var_2710');
INSERT INTO `turbine_model_points` VALUES (882, '20835', 1, 1, 1, 0, '1s平均风向', 'var_2709', 'F', '°', 'var_2709');
INSERT INTO `turbine_model_points` VALUES (883, '20835', 0, 0, 0, 0, '600s平均风向', 'var_2712', 'F', '°', 'var_2712');
INSERT INTO `turbine_model_points` VALUES (884, '20835', 0, 0, 0, 0, '盘车电机启动停机', 'var_2832', 'B', 'notdefined', 'var_2832');
INSERT INTO `turbine_model_points` VALUES (885, '20835', 0, 0, 0, 0, '1s平均风速过高停机', 'var_2833', 'B', 'notdefined', 'var_2833');
INSERT INTO `turbine_model_points` VALUES (886, '20835', 0, 0, 0, 0, '30s平均风速过高停机', 'var_2834', 'B', 'notdefined', 'var_2834');
INSERT INTO `turbine_model_points` VALUES (887, '20835', 0, 0, 0, 0, '600s平均风速过高停机', 'var_2835', 'B', 'notdefined', 'var_2835');
INSERT INTO `turbine_model_points` VALUES (888, '20835', 0, 0, 0, 0, '风速超出启动范围停机', 'var_2836', 'B', 'notdefined', 'var_2836');
INSERT INTO `turbine_model_points` VALUES (889, '20835', 0, 0, 0, 0, '600s平均风速过低停机', 'var_2837', 'B', 'notdefined', 'var_2837');
INSERT INTO `turbine_model_points` VALUES (890, '20835', 0, 0, 0, 0, '风机启动不成功停机', 'var_2838', 'B', 'notdefined', 'var_2838');
INSERT INTO `turbine_model_points` VALUES (891, '20835', 0, 0, 0, 0, '机组停机自检停机', 'var_2839', 'B', 'notdefined', 'var_2839');
INSERT INTO `turbine_model_points` VALUES (892, '20835', 0, 0, 0, 0, '变桨润滑条件OK停机', 'var_2840', 'B', 'notdefined', 'var_2840');
INSERT INTO `turbine_model_points` VALUES (893, '20835', 0, 0, 0, 0, '变桨润滑发电机超速报警停机', 'var_2841', 'B', 'notdefined', 'var_2841');
INSERT INTO `turbine_model_points` VALUES (894, '20835', 0, 0, 0, 0, '变桨润滑等待变桨移动停机', 'var_2842', 'B', 'notdefined', 'var_2842');
INSERT INTO `turbine_model_points` VALUES (895, '20835', 0, 0, 0, 0, '停机为变桨轴承润滑', 'var_2843', 'B', 'notdefined', 'var_2843');
INSERT INTO `turbine_model_points` VALUES (896, '20835', 0, 0, 0, 0, '变桨停机润滑停机', 'var_2846', 'B', 'notdefined', 'var_2846');
INSERT INTO `turbine_model_points` VALUES (897, '20835', 0, 0, 0, 0, '主变压器消防系统状态反馈', 'var_3012', 'B', 'notdefined', 'var_3012');
INSERT INTO `turbine_model_points` VALUES (898, '20835', 0, 0, 0, 0, '塔基柜消防系统状态反馈', 'var_3013', 'B', 'notdefined', 'var_3013');
INSERT INTO `turbine_model_points` VALUES (899, '20835', 0, 0, 0, 0, '变流器消防系统状态反馈', 'var_3014', 'B', 'notdefined', 'var_3014');
INSERT INTO `turbine_model_points` VALUES (900, '20835', 0, 0, 0, 0, '机舱控制柜消防系统状态反馈', 'var_3015', 'B', 'notdefined', 'var_3015');
INSERT INTO `turbine_model_points` VALUES (901, '20835', 0, 0, 0, 0, '机舱大空间消防系统状态反馈', 'var_3016', 'B', 'notdefined', 'var_3016');
INSERT INTO `turbine_model_points` VALUES (902, '20835', 0, 0, 0, 0, '主变压器消防激活控制', 'var_3017', 'B', 'notdefined', 'var_3017');
INSERT INTO `turbine_model_points` VALUES (903, '20835', 0, 0, 0, 0, '塔基柜消防激活控制', 'var_3018', 'B', 'notdefined', 'var_3018');
INSERT INTO `turbine_model_points` VALUES (904, '20835', 0, 0, 0, 0, '变流器消防激活控制', 'var_3019', 'B', 'notdefined', 'var_3019');
INSERT INTO `turbine_model_points` VALUES (905, '20835', 0, 0, 0, 0, '机舱消防激活控制', 'var_3020', 'B', 'notdefined', 'var_3020');
INSERT INTO `turbine_model_points` VALUES (906, '20835', 0, 0, 0, 0, '机舱大空间消防系统激活控制', 'var_3021', 'B', 'notdefined', 'var_3021');
INSERT INTO `turbine_model_points` VALUES (907, '20835', 0, 0, 0, 0, '主变压器火灾一级报警', 'var_3022', 'B', 'notdefined', 'var_3022');
INSERT INTO `turbine_model_points` VALUES (908, '20835', 0, 0, 0, 0, '塔基控制柜火灾一级报警', 'var_3024', 'B', 'notdefined', 'var_3024');
INSERT INTO `turbine_model_points` VALUES (909, '20835', 0, 0, 0, 0, '变流器火灾一级报警', 'var_3025', 'B', 'notdefined', 'var_3025');
INSERT INTO `turbine_model_points` VALUES (910, '20835', 0, 0, 0, 0, '机舱控制柜火灾一级报警', 'var_3026', 'B', 'notdefined', 'var_3026');
INSERT INTO `turbine_model_points` VALUES (911, '20835', 0, 0, 0, 0, '机舱大空间火灾一级报警', 'var_3027', 'B', 'notdefined', 'var_3027');
INSERT INTO `turbine_model_points` VALUES (912, '20835', 0, 0, 0, 0, '主变压器火灾二级报警', 'var_3028', 'B', 'notdefined', 'var_3028');
INSERT INTO `turbine_model_points` VALUES (913, '20835', 0, 0, 0, 0, '塔基控制柜火灾二级报警', 'var_3030', 'B', 'notdefined', 'var_3030');
INSERT INTO `turbine_model_points` VALUES (914, '20835', 0, 0, 0, 0, '变流器火灾二级报警', 'var_3031', 'B', 'notdefined', 'var_3031');
INSERT INTO `turbine_model_points` VALUES (915, '20835', 0, 0, 0, 0, '机舱控制柜火灾二级报警', 'var_3032', 'B', 'notdefined', 'var_3032');
INSERT INTO `turbine_model_points` VALUES (916, '20835', 0, 0, 0, 0, '机舱大空间火灾二级报警', 'var_3033', 'B', 'notdefined', 'var_3033');
INSERT INTO `turbine_model_points` VALUES (917, '20835', 1, 0, 1, 0, '工作模式', 'workMode', 'I', 'notdefined', 'workMode');
INSERT INTO `turbine_model_points` VALUES (918, '20835', 0, 0, 0, 0, '通讯状态', 'comState', 'I', 'notdefined', 'comState');
INSERT INTO `turbine_model_points` VALUES (919, '20835', 0, 0, 0, 0, '停运小时数', 'hourStop', 'I', 'h', 'hourStop');
INSERT INTO `turbine_model_points` VALUES (920, '20835', 0, 0, 0, 0, '主控版本字段1', 'var_10000', 'I', 'notdefined', 'var_10000');
INSERT INTO `turbine_model_points` VALUES (921, '20835', 0, 0, 0, 0, '主控版本字段2', 'var_10001', 'I', 'notdefined', 'var_10001');
INSERT INTO `turbine_model_points` VALUES (922, '20835', 0, 0, 0, 0, '主控版本字段3', 'var_10002', 'I', 'notdefined', 'var_10002');
INSERT INTO `turbine_model_points` VALUES (923, '20835', 0, 0, 0, 0, '主控版本字段4', 'var_10003', 'I', 'notdefined', 'var_10003');
INSERT INTO `turbine_model_points` VALUES (924, '20835', 0, 0, 0, 0, '1#叶片变桨驱动器故障代码', 'var_13063', 'I', 'notdefined', 'var_13063');
INSERT INTO `turbine_model_points` VALUES (925, '20835', 0, 0, 0, 0, '变流器首故障代码', 'converterFaultCode', 'I', 'notdefined', 'converterFaultCode');
INSERT INTO `turbine_model_points` VALUES (926, '20835', 0, 0, 0, 0, '不可用信息时间', 'iu', 'F', 'h', 'iu');
INSERT INTO `turbine_model_points` VALUES (927, '20835', 0, 0, 0, 0, '理论功率', 'theoryPower', 'F', 'kW', 'theoryPower');
INSERT INTO `turbine_model_points` VALUES (928, '20835', 0, 0, 0, 0, '强制停机-故障检修时间', 'var_3001', 'F', 'h', 'var_3001');
INSERT INTO `turbine_model_points` VALUES (929, '20835', 0, 0, 0, 0, '强制停机-故障停机时间', 'var_3000', 'F', 'h', 'var_3000');
INSERT INTO `turbine_model_points` VALUES (930, '20835', 0, 0, 0, 0, '3#叶片变桨电机转矩', 'var_12033', 'F', 'Nm', 'var_12033');
INSERT INTO `turbine_model_points` VALUES (931, '20835', 0, 0, 0, 0, '1#叶片变桨电机转矩', 'var_12031', 'F', 'Nm', 'var_12031');
INSERT INTO `turbine_model_points` VALUES (932, '20835', 1, 0, 0, 0, '变流器机侧C相电流', 'var_15006', 'F', 'A', 'var_15006');
INSERT INTO `turbine_model_points` VALUES (933, '20835', 1, 0, 0, 0, '变流器机侧B相电流', 'var_15005', 'F', 'A', 'var_15005');
INSERT INTO `turbine_model_points` VALUES (934, '20835', 1, 0, 0, 0, '变流器机侧A相电流', 'var_15004', 'F', 'A', 'var_15004');
INSERT INTO `turbine_model_points` VALUES (935, '20835', 0, 0, 0, 0, '变流器总电流', 'var_15002', 'F', 'A', 'var_15002');
INSERT INTO `turbine_model_points` VALUES (936, '20835', 1, 1, 0, 0, '变流器入水口温度反馈', 'var_12016', 'F', '°C', 'var_12016');
INSERT INTO `turbine_model_points` VALUES (937, '20835', 0, 0, 0, 0, '变流器入水口压力反馈', 'var_12015', 'F', 'bar', 'var_12015');
INSERT INTO `turbine_model_points` VALUES (938, '20835', 0, 0, 0, 0, '强制停机状态', 'var_1064', 'B', 'notdefined', 'var_1064');
INSERT INTO `turbine_model_points` VALUES (939, '20835', 0, 0, 0, 0, '定期维护使能', 'var_1065', 'B', 'notdefined', 'var_1065');
INSERT INTO `turbine_model_points` VALUES (940, '20835', 0, 0, 0, 0, '计划性改进使能', 'var_1066', 'B', 'notdefined', 'var_1066');
INSERT INTO `turbine_model_points` VALUES (941, '20835', 0, 0, 0, 0, '不可抗力使能', 'var_1067', 'B', 'notdefined', 'var_1067');
INSERT INTO `turbine_model_points` VALUES (942, '20835', 0, 0, 0, 0, '暂停作业使能', 'var_1068', 'B', 'notdefined', 'var_1068');
INSERT INTO `turbine_model_points` VALUES (943, '20835', 0, 0, 0, 0, '正常发电运行状态', 'var_1069', 'B', 'notdefined', 'var_1069');
INSERT INTO `turbine_model_points` VALUES (944, '20835', 0, 0, 0, 0, '降额运行状态', 'lowRateSingle', 'B', 'notdefined', 'lowRateSingle');
INSERT INTO `turbine_model_points` VALUES (945, '20835', 0, 0, 0, 0, '降级运行状态', 'lowLevelSingle', 'B', 'notdefined', 'lowLevelSingle');
INSERT INTO `turbine_model_points` VALUES (946, '20835', 0, 0, 0, 0, '技术待机状态', 'var_1072', 'B', 'notdefined', 'var_1072');
INSERT INTO `turbine_model_points` VALUES (947, '20835', 0, 0, 0, 0, '无风状态', 'var_1073', 'B', 'notdefined', 'var_1073');
INSERT INTO `turbine_model_points` VALUES (948, '20835', 0, 0, 0, 0, '超出其他环境状态', 'var_1074', 'B', 'notdefined', 'var_1074');
INSERT INTO `turbine_model_points` VALUES (949, '20835', 0, 0, 0, 0, '指令停机状态', 'var_1075', 'B', 'notdefined', 'var_1075');
INSERT INTO `turbine_model_points` VALUES (950, '20835', 0, 0, 0, 0, '超出电气范围状态', 'var_1076', 'B', 'notdefined', 'var_1076');
INSERT INTO `turbine_model_points` VALUES (951, '20835', 0, 0, 0, 0, 'C3柜接地开关状态', 'var_28353', 'B', 'notdefined', 'var_28353');
INSERT INTO `turbine_model_points` VALUES (952, '20835', 0, 0, 0, 0, 'C3柜就地状态', 'var_28354', 'B', 'notdefined', 'var_28354');
INSERT INTO `turbine_model_points` VALUES (953, '20835', 0, 0, 0, 0, '环网柜断路器未储能状态', 'var_28355', 'B', 'notdefined', 'var_28355');
INSERT INTO `turbine_model_points` VALUES (954, '20835', 0, 0, 0, 0, '变压器重瓦斯跳闸开关断线反馈', 'var_28356', 'B', 'notdefined', 'var_28356');
INSERT INTO `turbine_model_points` VALUES (955, '20835', 0, 0, 0, 0, '变压器超温跳闸开关断线反馈', 'var_28357', 'B', 'notdefined', 'var_28357');
INSERT INTO `turbine_model_points` VALUES (956, '20835', 0, 0, 0, 0, '变压器压力阀跳闸开关断线反馈', 'var_28358', 'B', 'notdefined', 'var_28358');
INSERT INTO `turbine_model_points` VALUES (957, '20835', 0, 0, 0, 0, '环网柜断路器闭锁信号反馈', 'var_28359', 'B', 'notdefined', 'var_28359');
INSERT INTO `turbine_model_points` VALUES (958, '20835', 0, 0, 0, 0, '环网柜断路器机构报警信号反馈', 'var_28360', 'B', 'notdefined', 'var_28360');
INSERT INTO `turbine_model_points` VALUES (959, '20835', 0, 0, 0, 0, 'SCADA下发抗台预警激活', 'var_28361', 'B', 'notdefined', 'var_28361');
INSERT INTO `turbine_model_points` VALUES (960, '20835', 0, 0, 0, 0, 'SCADA下发抗台预警激活主控反馈', 'var_28362', 'B', 'notdefined', 'var_28362');
INSERT INTO `turbine_model_points` VALUES (961, '20835', 0, 0, 0, 0, 'SCADA下发抗台预警取消', 'var_28363', 'B', 'notdefined', 'var_28363');
INSERT INTO `turbine_model_points` VALUES (962, '20835', 0, 0, 0, 0, 'SCADA下发抗台预警取消主控反馈', 'var_28364', 'B', 'notdefined', 'var_28364');
INSERT INTO `turbine_model_points` VALUES (963, '20835', 0, 0, 0, 0, 'SCADA下发抗台过境激活', 'var_28365', 'B', 'notdefined', 'var_28365');
INSERT INTO `turbine_model_points` VALUES (964, '20835', 0, 0, 0, 0, 'SCADA下发抗台过境激活主控反馈', 'var_28366', 'B', 'notdefined', 'var_28366');
INSERT INTO `turbine_model_points` VALUES (965, '20835', 0, 0, 0, 0, 'SCADA下发抗台过境取消', 'var_28367', 'B', 'notdefined', 'var_28367');
INSERT INTO `turbine_model_points` VALUES (966, '20835', 0, 0, 0, 0, 'SCADA下发抗台过境取消主控反馈', 'var_28368', 'B', 'notdefined', 'var_28368');
INSERT INTO `turbine_model_points` VALUES (967, '20835', 0, 0, 0, 0, 'SCADA下发抗台模拟测试启动', 'var_28369', 'B', 'notdefined', 'var_28369');
INSERT INTO `turbine_model_points` VALUES (968, '20835', 0, 0, 0, 0, 'SCADA下发抗台模拟测试启动主控反馈', 'var_28370', 'B', 'notdefined', 'var_28370');
INSERT INTO `turbine_model_points` VALUES (969, '20835', 0, 0, 0, 0, 'SCADA下发抗台模拟测试退出', 'var_28371', 'B', 'notdefined', 'var_28371');
INSERT INTO `turbine_model_points` VALUES (970, '20835', 0, 0, 0, 0, 'SCADA下发抗台模拟测试退出主控反馈', 'var_28372', 'B', 'notdefined', 'var_28372');
INSERT INTO `turbine_model_points` VALUES (971, '20835', 0, 0, 0, 0, 'SCADA下发抗台策略2执行', 'var_28373', 'B', 'notdefined', 'var_28373');
INSERT INTO `turbine_model_points` VALUES (972, '20835', 0, 0, 0, 0, 'SCADA下发抗台策略2执行主控反馈', 'var_28374', 'B', 'notdefined', 'var_28374');
INSERT INTO `turbine_model_points` VALUES (973, '20835', 0, 0, 0, 0, '电网掉电标志', 'var_28375', 'B', 'notdefined', 'var_28375');
INSERT INTO `turbine_model_points` VALUES (974, '20835', 0, 0, 0, 0, 'SCADA下发计划性停电指令', 'var_28376', 'B', 'notdefined', 'var_28376');
INSERT INTO `turbine_model_points` VALUES (975, '20835', 0, 0, 0, 0, '后备电源启动', 'var_28377', 'B', 'notdefined', 'var_28377');
INSERT INTO `turbine_model_points` VALUES (976, '20835', 0, 0, 0, 0, '后备电源离网供电模式', 'var_28378', 'B', 'notdefined', 'var_28378');
INSERT INTO `turbine_model_points` VALUES (977, '20835', 0, 0, 0, 0, '风速异常', 'winSpdErr', 'B', 'notdefined', 'winSpdErr');
INSERT INTO `turbine_model_points` VALUES (978, '20835', 0, 0, 0, 0, '变压器门位置信号', 'var_1708', 'B', 'notdefined', 'var_1708');
INSERT INTO `turbine_model_points` VALUES (979, '20835', 0, 0, 0, 0, '总反向无功电能', 'var_15058', 'F', 'kVArh', 'var_15058');
INSERT INTO `turbine_model_points` VALUES (980, '20835', 0, 0, 0, 0, '总反向有功电能', 'var_15057', 'F', 'kWh', 'var_15057');
INSERT INTO `turbine_model_points` VALUES (981, '20835', 0, 0, 0, 0, '总正向无功电能', 'var_15056', 'F', 'kVArh', 'var_15056');
INSERT INTO `turbine_model_points` VALUES (982, '20835', 0, 0, 0, 0, '总正向有功电能', 'var_15055', 'F', 'kWh', 'var_15055');
INSERT INTO `turbine_model_points` VALUES (983, '20835', 0, 0, 0, 0, '技术待机时间', 'iaongts', 'F', 'h', 'iaongts');
INSERT INTO `turbine_model_points` VALUES (984, '20835', 0, 0, 0, 0, '降级时间', 'iaogppJj', 'F', 'h', 'iaogppJj');
INSERT INTO `turbine_model_points` VALUES (985, '20835', 0, 0, 0, 0, '降额时间', 'iaogppJe', 'F', 'h', 'iaogppJe');
INSERT INTO `turbine_model_points` VALUES (986, '20835', 0, 0, 0, 0, '3#叶片X方向加速度', 'var_15019', 'F', 'g', 'var_15019');
INSERT INTO `turbine_model_points` VALUES (987, '20835', 0, 0, 0, 0, '2#叶片X方向加速度', 'var_15018', 'F', 'g', 'var_15018');
INSERT INTO `turbine_model_points` VALUES (988, '20835', 0, 0, 0, 0, '1#叶片X方向加速度', 'var_15017', 'F', 'g', 'var_15017');
INSERT INTO `turbine_model_points` VALUES (989, '20835', 0, 0, 0, 0, '变流器总无功功率', 'var_15016', 'F', 'kVAr', 'var_15016');
INSERT INTO `turbine_model_points` VALUES (990, '20835', 0, 0, 0, 0, '变流器电网电压', 'var_15015', 'F', 'V', 'var_15015');
INSERT INTO `turbine_model_points` VALUES (991, '20835', 0, 0, 0, 0, '变流器网侧B相无功电流', 'var_15013', 'F', 'A', 'var_15013');
INSERT INTO `turbine_model_points` VALUES (992, '20835', 0, 0, 0, 0, '变流器网侧A相无功电流', 'var_15012', 'F', 'A', 'var_15012');
INSERT INTO `turbine_model_points` VALUES (993, '20835', 0, 0, 0, 0, '变流器网侧C相有功电流', 'var_15011', 'F', 'A', 'var_15011');
INSERT INTO `turbine_model_points` VALUES (994, '20835', 0, 0, 0, 0, '变流器网侧B相有功电流', 'var_15010', 'F', 'A', 'var_15010');
INSERT INTO `turbine_model_points` VALUES (995, '20835', 0, 0, 0, 0, '变流器网侧A相有功电流', 'var_15009', 'F', 'A', 'var_15009');
INSERT INTO `turbine_model_points` VALUES (996, '20835', 0, 0, 0, 0, '变流器电网频率', 'var_15008', 'F', 'Hz', 'var_15008');
INSERT INTO `turbine_model_points` VALUES (997, '20835', 0, 0, 0, 0, '变流器发电机转速1s平均反馈', 'var_15007', 'F', 'RPM', 'var_15007');
INSERT INTO `turbine_model_points` VALUES (998, '20835', 0, 0, 0, 0, 'C2柜就地状态', 'var_1719', 'B', 'notdefined', 'var_1719');
INSERT INTO `turbine_model_points` VALUES (999, '20835', 0, 0, 0, 0, 'C2柜高压负荷分位', 'var_1720', 'B', 'notdefined', 'var_1720');
INSERT INTO `turbine_model_points` VALUES (1000, '20835', 0, 0, 0, 0, 'C2柜高压负荷合位', 'var_1731', 'B', 'notdefined', 'var_1731');
INSERT INTO `turbine_model_points` VALUES (1001, '20835', 0, 0, 0, 0, 'C2柜接地开关状态', 'var_1732', 'B', 'notdefined', 'var_1732');
INSERT INTO `turbine_model_points` VALUES (1002, '20835', 0, 0, 0, 0, 'C2柜高压负荷开关控制合闸', 'var_1795', 'B', 'notdefined', 'var_1795');
INSERT INTO `turbine_model_points` VALUES (1003, '20835', 0, 0, 0, 0, 'C2柜高压负荷开关控制分闸', 'var_1796', 'B', 'notdefined', 'var_1796');
INSERT INTO `turbine_model_points` VALUES (1004, '20835', 0, 0, 0, 0, 'C1柜高压负荷开关控制合闸', 'var_1797', 'B', 'notdefined', 'var_1797');
INSERT INTO `turbine_model_points` VALUES (1005, '20835', 0, 0, 0, 0, 'C1柜高压负荷开关控制分闸', 'var_1798', 'B', 'notdefined', 'var_1798');
INSERT INTO `turbine_model_points` VALUES (1006, '20835', 0, 0, 0, 0, 'V柜断路器控制合闸', 'var_1799', 'B', 'notdefined', 'var_1799');
INSERT INTO `turbine_model_points` VALUES (1007, '20835', 0, 0, 0, 0, 'V柜断路器控制分闸', 'var_1800', 'B', 'notdefined', 'var_1800');
INSERT INTO `turbine_model_points` VALUES (1008, '20835', 0, 0, 0, 0, '抗台模式状态', 'typhoonState', 'I', 'notdefined', 'typhoonState');
INSERT INTO `turbine_model_points` VALUES (1009, '20835', 0, 0, 0, 0, '偏航电机故障代码', 'var_1883', 'I', 'notdefined', 'var_1883');
INSERT INTO `turbine_model_points` VALUES (1010, '20835', 0, 0, 0, 0, '液压系统液压泵1运行超时故障', 'var_2367', 'B', 'notdefined', 'var_2367');
INSERT INTO `turbine_model_points` VALUES (1011, '20835', 0, 0, 0, 0, '安全控制器故障代码', 'var_2717', 'I', 'notdefined', 'var_2717');
INSERT INTO `turbine_model_points` VALUES (1012, '20835', 0, 0, 0, 0, 'C3柜高压负荷开关控制分闸', 'var_28351', 'B', 'notdefined', 'var_28351');
INSERT INTO `turbine_model_points` VALUES (1013, '20835', 0, 0, 0, 0, 'C3柜高压负荷开关控制合闸', 'var_28352', 'B', 'notdefined', 'var_28352');
INSERT INTO `turbine_model_points` VALUES (1014, '20835', 1, 0, 1, 0, '限功率运行状态', 'limitPowBool', 'B', 'notdefined', 'limitPowBool');
INSERT INTO `turbine_model_points` VALUES (1015, '20835', 0, 0, 0, 0, '后备电源故障警告', 'var_38513', 'B', 'notdefined', 'var_38513');
INSERT INTO `turbine_model_points` VALUES (1016, '20835', 0, 0, 0, 0, '后备电源警告', 'var_38514', 'B', 'notdefined', 'var_38514');
INSERT INTO `turbine_model_points` VALUES (1017, '20835', 0, 0, 0, 0, '后备电源故障', 'var_38515', 'B', 'notdefined', 'var_38515');
INSERT INTO `turbine_model_points` VALUES (1018, '20835', 0, 0, 0, 0, '抗台模拟测试失败故障', 'var_38516', 'B', 'notdefined', 'var_38516');
INSERT INTO `turbine_model_points` VALUES (1019, '20835', 0, 0, 0, 0, '变压器W相绕组温度', 'var_1723', 'F', '°C', 'var_1723');
INSERT INTO `turbine_model_points` VALUES (1020, '20835', 0, 0, 0, 0, '变压器超温跳闸故障', 'var_3003', 'B', 'notdefined', 'var_3003');
INSERT INTO `turbine_model_points` VALUES (1021, '20835', 0, 0, 0, 0, '变压器超温报警', 'var_3004', 'B', 'notdefined', 'var_3004');
INSERT INTO `turbine_model_points` VALUES (1022, '20835', 0, 0, 0, 0, '气体继电器轻瓦斯信号', 'var_3005', 'B', 'notdefined', 'var_3005');
INSERT INTO `turbine_model_points` VALUES (1023, '20835', 0, 0, 0, 0, '气体继电器重瓦斯信号', 'var_3006', 'B', 'notdefined', 'var_3006');
INSERT INTO `turbine_model_points` VALUES (1024, '20835', 0, 0, 0, 0, '压力跳闸', 'var_3008', 'B', 'notdefined', 'var_3008');
INSERT INTO `turbine_model_points` VALUES (1025, '20835', 0, 0, 0, 0, '低油位信号', 'var_3009', 'B', 'notdefined', 'var_3009');
INSERT INTO `turbine_model_points` VALUES (1026, '20835', 0, 0, 0, 0, '油泵超温信号', 'var_3010', 'B', 'notdefined', 'var_3010');
INSERT INTO `turbine_model_points` VALUES (1027, '20835', 0, 0, 0, 0, '油泵电机过载', 'var_3011', 'B', 'notdefined', 'var_3011');
INSERT INTO `turbine_model_points` VALUES (1028, '20835', 0, 0, 0, 0, '压力释放阀动作信号', 'var_3007', 'B', 'notdefined', 'var_3007');
INSERT INTO `turbine_model_points` VALUES (1029, '20835', 0, 0, 0, 0, 'V柜就地状态', 'var_1710', 'B', 'notdefined', 'var_1710');
INSERT INTO `turbine_model_points` VALUES (1030, '20835', 0, 0, 0, 0, 'V柜断路器分位', 'var_1711', 'B', 'notdefined', 'var_1711');
INSERT INTO `turbine_model_points` VALUES (1031, '20835', 0, 0, 0, 0, 'V柜断路器合位', 'var_1712', 'B', 'notdefined', 'var_1712');
INSERT INTO `turbine_model_points` VALUES (1032, '20835', 0, 0, 0, 0, 'V柜接地开关状态', 'var_1713', 'B', 'notdefined', 'var_1713');
INSERT INTO `turbine_model_points` VALUES (1033, '20835', 0, 0, 0, 0, 'C1柜就地状态', 'var_1715', 'B', 'notdefined', 'var_1715');
INSERT INTO `turbine_model_points` VALUES (1034, '20835', 0, 0, 0, 0, 'C1柜高压负荷分位', 'var_1716', 'B', 'notdefined', 'var_1716');
INSERT INTO `turbine_model_points` VALUES (1035, '20835', 0, 0, 0, 0, 'C1柜高压负荷合位', 'var_1717', 'B', 'notdefined', 'var_1717');
INSERT INTO `turbine_model_points` VALUES (1036, '20835', 0, 0, 0, 0, 'C1柜接地开关状态', 'var_1718', 'B', 'notdefined', 'var_1718');
INSERT INTO `turbine_model_points` VALUES (1037, '20835', 0, 0, 0, 0, '后备电源电池健康状态', 'var_18364', 'F', '%', 'var_18364');
INSERT INTO `turbine_model_points` VALUES (1038, '20835', 0, 0, 0, 0, '后备电源电池荷电状态', 'var_18363', 'F', '%', 'var_18363');
INSERT INTO `turbine_model_points` VALUES (1039, '20835', 0, 0, 0, 0, '后备电源电池放电可用电量', 'var_18362', 'F', 'kWh', 'var_18362');
INSERT INTO `turbine_model_points` VALUES (1040, '20835', 0, 0, 0, 0, '后备电源柜内温度', 'var_18361', 'F', '℃', 'var_18361');
INSERT INTO `turbine_model_points` VALUES (1041, '20835', 0, 0, 0, 0, '后备电源电池电流', 'var_18360', 'F', 'A', 'var_18360');
INSERT INTO `turbine_model_points` VALUES (1042, '20835', 0, 0, 0, 0, '后备电源电池电压', 'var_18359', 'F', 'V', 'var_18359');
INSERT INTO `turbine_model_points` VALUES (1043, '20835', 0, 0, 0, 0, '后备电源网测无功功率', 'var_18358', 'F', 'kVar', 'var_18358');
INSERT INTO `turbine_model_points` VALUES (1044, '20835', 0, 0, 0, 0, '后备电源网测有功功率', 'var_18357', 'F', 'kW', 'var_18357');
INSERT INTO `turbine_model_points` VALUES (1045, '20835', 0, 0, 0, 0, '后备电源网测电压', 'var_18356', 'F', 'V', 'var_18356');
INSERT INTO `turbine_model_points` VALUES (1046, '20835', 0, 0, 0, 0, '后备电源网测电流', 'var_18355', 'F', 'A', 'var_18355');
INSERT INTO `turbine_model_points` VALUES (1047, '20835', 0, 0, 0, 0, '10min平均风速SCADA下发值', 'var_18353', 'F', 'm/s', 'var_18353');
INSERT INTO `turbine_model_points` VALUES (1048, '20835', 0, 0, 0, 0, '顶层油温', 'var_3002', 'F', '°C', 'var_3002');
INSERT INTO `turbine_model_points` VALUES (1049, '20835', 0, 0, 0, 0, '变压器V相绕组温度', 'var_1722', 'F', '°C', 'var_1722');
INSERT INTO `turbine_model_points` VALUES (1050, '20835', 0, 0, 0, 0, '变压器U相绕组温度', 'var_1721', 'F', '°C', 'var_1721');
INSERT INTO `turbine_model_points` VALUES (1051, '20835', 0, 0, 0, 0, '变压器风扇运行状态', 'var_1707', 'B', 'notdefined', 'var_1707');
INSERT INTO `turbine_model_points` VALUES (1052, '20835', 0, 0, 0, 0, 'V柜隔离开关状态', 'var_1714', 'B', 'notdefined', 'var_1714');
INSERT INTO `turbine_model_points` VALUES (1053, '20835', 0, 0, 0, 0, '变桨系统3#叶片直流母线电压', 'var_18027', 'F', 'notdefined', 'var_18027');
INSERT INTO `turbine_model_points` VALUES (1054, '20835', 0, 0, 0, 0, '变流器网侧C相无功电流', 'var_15014', 'F', 'A', 'var_15014');
INSERT INTO `turbine_model_points` VALUES (1055, '20835', 0, 0, 0, 0, '机组视在月损耗电量', 'var_2694', 'F', 'notdefined', 'var_2694');
INSERT INTO `turbine_model_points` VALUES (1056, '20835', 0, 0, 0, 0, '机组自损耗视在功率', 'var_2693', 'F', 'kVA', 'var_2693');
INSERT INTO `turbine_model_points` VALUES (1057, '20835', 0, 0, 0, 0, '机组无功总损耗电量', 'var_2692', 'F', 'kVArh', 'var_2692');
INSERT INTO `turbine_model_points` VALUES (1058, '20835', 0, 0, 0, 0, '机组无功月损耗电量', 'var_2691', 'F', 'notdefined', 'var_2691');
INSERT INTO `turbine_model_points` VALUES (1059, '20835', 1, 0, 0, 0, '机组自损耗无功功率', 'var_2690', 'F', 'kVAr', 'var_2690');
INSERT INTO `turbine_model_points` VALUES (1060, '20835', 0, 0, 0, 0, '机组有功总损耗电量', 'var_2689', 'F', 'kWh', 'var_2689');
INSERT INTO `turbine_model_points` VALUES (1061, '20835', 0, 0, 0, 0, '机组有功月损耗电量', 'var_2688', 'F', 'kW', 'var_2688');
INSERT INTO `turbine_model_points` VALUES (1062, '20835', 1, 0, 0, 0, '机组自损耗有功功率', 'var_2687', 'F', 'kW', 'var_2687');
INSERT INTO `turbine_model_points` VALUES (1063, '20835', 0, 0, 0, 0, '10s平均有功功率', 'var_2686', 'F', 'kW', 'var_2686');
INSERT INTO `turbine_model_points` VALUES (1064, '20835', 0, 0, 0, 0, '电网模块2无功功率', 'var_2685', 'F', 'kVAr', 'var_2685');
INSERT INTO `turbine_model_points` VALUES (1065, '20835', 0, 0, 0, 0, '电网模块2有功功率', 'var_2684', 'F', 'kW', 'var_2684');
INSERT INTO `turbine_model_points` VALUES (1066, '20835', 0, 0, 0, 0, '电网模块1无功功率', 'var_2683', 'F', 'kVAr', 'var_2683');
INSERT INTO `turbine_model_points` VALUES (1067, '20835', 0, 0, 0, 0, '电网模块1有功功率', 'var_2682', 'F', 'kW', 'var_2682');
INSERT INTO `turbine_model_points` VALUES (1068, '20835', 1, 0, 0, 0, '2#叶片变桨速度', 'var_2680', 'F', '°/s', 'var_2680');
INSERT INTO `turbine_model_points` VALUES (1069, '20835', 0, 0, 0, 0, '叶片应变桨的角度', 'var_100', 'F', '°', 'var_100');
INSERT INTO `turbine_model_points` VALUES (1070, '20835', 1, 0, 0, 0, '3#叶片冗余变桨角度', 'var_106', 'F', '°', 'var_106');
INSERT INTO `turbine_model_points` VALUES (1071, '20835', 1, 0, 0, 0, '2#叶片冗余变桨角度', 'var_105', 'F', '°', 'var_105');
INSERT INTO `turbine_model_points` VALUES (1072, '20835', 1, 0, 0, 0, '1#叶片冗余变桨角度', 'var_104', 'F', '°', 'var_104');
INSERT INTO `turbine_model_points` VALUES (1073, '20835', 0, 0, 0, 0, '3#叶片驱动电流', 'var_112', 'F', 'A', 'var_112');
INSERT INTO `turbine_model_points` VALUES (1074, '20835', 0, 0, 0, 0, '2#叶片驱动电流', 'var_111', 'F', 'A', 'var_111');
INSERT INTO `turbine_model_points` VALUES (1075, '20835', 0, 0, 0, 0, '1#叶片驱动电流', 'var_110', 'F', 'A', 'var_110');
INSERT INTO `turbine_model_points` VALUES (1076, '20835', 0, 0, 0, 0, '变压器冷却液进口压力', 'var_1889', 'F', 'Bar', 'var_1889');
INSERT INTO `turbine_model_points` VALUES (1077, '20835', 0, 0, 0, 0, '发电机冷却液进口压力', 'var_1888', 'F', 'bar', 'var_1888');
INSERT INTO `turbine_model_points` VALUES (1078, '20835', 0, 0, 0, 0, '变频器4冷却液进口压力', 'var_1887', 'F', 'Bar', 'var_1887');
INSERT INTO `turbine_model_points` VALUES (1079, '20835', 0, 0, 0, 0, '变频器3冷却液进口压力', 'var_1886', 'F', 'Bar', 'var_1886');
INSERT INTO `turbine_model_points` VALUES (1080, '20835', 0, 0, 0, 0, '变频器2冷却液进口压力', 'var_1885', 'F', 'Bar', 'var_1885');
INSERT INTO `turbine_model_points` VALUES (1081, '20835', 0, 0, 0, 0, '变频器1冷却液进口压力', 'var_1884', 'F', 'Bar', 'var_1884');
INSERT INTO `turbine_model_points` VALUES (1082, '20835', 1, 1, 1, 0, '机舱X方向振动', 'var_382', 'F', 'm/s^2', 'var_382');
INSERT INTO `turbine_model_points` VALUES (1083, '20835', 0, 0, 0, 0, '变频器进口水温4', 'var_1840', 'F', '°C', 'var_1840');
INSERT INTO `turbine_model_points` VALUES (1084, '20835', 0, 0, 0, 0, '变频器进口水温3', 'var_1839', 'F', '°C', 'var_1839');
INSERT INTO `turbine_model_points` VALUES (1085, '20835', 0, 0, 0, 0, '变频器进口水温2', 'var_1838', 'F', '°C', 'var_1838');
INSERT INTO `turbine_model_points` VALUES (1086, '20835', 0, 0, 0, 0, '变频器进口水温1', 'var_1837', 'F', '°C', 'var_1837');
INSERT INTO `turbine_model_points` VALUES (1087, '20835', 0, 0, 0, 0, '变频器机侧电流', 'var_1835', 'F', 'A', 'var_1835');
INSERT INTO `turbine_model_points` VALUES (1088, '20835', 0, 0, 0, 0, '机舱与风向夹角', 'var_1834', 'F', '°', 'var_1834');
INSERT INTO `turbine_model_points` VALUES (1089, '20835', 0, 0, 0, 0, '曲线-60s平均功率', 'powCurvePowerAct', 'F', 'kW', 'powCurvePowerAct');
INSERT INTO `turbine_model_points` VALUES (1090, '20835', 0, 0, 0, 0, '曲线-60s平均风速', 'powCurveWinSpd', 'F', 'm/s', 'powCurveWinSpd');
INSERT INTO `turbine_model_points` VALUES (1091, '20835', 0, 0, 0, 0, '60s平均空气密度', 'powCurveDensity', 'F', 'kg/m^3', 'powCurveDensity');
INSERT INTO `turbine_model_points` VALUES (1092, '20835', 0, 0, 0, 0, '自动降容功率设置反馈值', 'var_56', 'F', 'H/L', 'var_56');
INSERT INTO `turbine_model_points` VALUES (1093, '20835', 0, 0, 0, 0, '10s平均有功功率（带自耗）', 'var_42', 'F', 'kW', 'var_42');
INSERT INTO `turbine_model_points` VALUES (1094, '20835', 0, 0, 0, 0, '60s平均有功功率', 'var_40', 'F', 'kW', 'var_40');
INSERT INTO `turbine_model_points` VALUES (1095, '20835', 0, 0, 0, 0, '空气密度反馈值', 'var_60', 'F', 'notdefined', 'var_60');
INSERT INTO `turbine_model_points` VALUES (1096, '20835', 0, 0, 0, 0, '空气密度下发值', 'var_59', 'F', 'notdefined', 'var_59');
INSERT INTO `turbine_model_points` VALUES (1097, '20835', 0, 0, 0, 0, '变压器冷却液进口温度', 'var_1724', 'F', '°C', 'var_1724');
INSERT INTO `turbine_model_points` VALUES (1098, '20835', 0, 0, 0, 0, '液压站1主系统压力', 'var_1742', 'F', 'Bar', 'var_1742');
INSERT INTO `turbine_model_points` VALUES (1099, '20835', 0, 0, 0, 0, '塔基温度', 'var_1159', 'F', '°C', 'var_1159');
INSERT INTO `turbine_model_points` VALUES (1100, '20835', 0, 0, 0, 0, '10s平均风速', 'var_357', 'F', 'm/s', 'var_357');
INSERT INTO `turbine_model_points` VALUES (1101, '20835', 0, 0, 0, 0, '电网频率2', 'var_258', 'F', 'Hz', 'var_258');
INSERT INTO `turbine_model_points` VALUES (1102, '20835', 0, 0, 0, 0, '3#叶片电机温度', 'var_115', 'F', '°C', 'var_115');
INSERT INTO `turbine_model_points` VALUES (1103, '20835', 0, 0, 0, 0, '2#叶片电机温度', 'var_114', 'F', '°C', 'var_114');
INSERT INTO `turbine_model_points` VALUES (1104, '20835', 0, 0, 0, 0, '1#叶片电机温度', 'var_113', 'F', '°C', 'var_113');
INSERT INTO `turbine_model_points` VALUES (1105, '20835', 0, 0, 0, 0, '3#叶片控制柜温度', 'var_118', 'F', '°C', 'var_118');
INSERT INTO `turbine_model_points` VALUES (1106, '20835', 0, 0, 0, 0, '2#叶片控制柜温度', 'var_117', 'F', '°C', 'var_117');
INSERT INTO `turbine_model_points` VALUES (1107, '20835', 0, 0, 0, 0, '1#叶片控制柜温度', 'var_116', 'F', '°C', 'var_116');
INSERT INTO `turbine_model_points` VALUES (1108, '20835', 0, 0, 0, 0, '3#叶片后备电源电压', 'var_131', 'F', 'V', 'var_131');
INSERT INTO `turbine_model_points` VALUES (1109, '20835', 0, 0, 0, 0, '2#叶片后备电源电压', 'var_130', 'F', 'V', 'var_130');
INSERT INTO `turbine_model_points` VALUES (1110, '20835', 0, 0, 0, 0, '1#叶片后备电源电压', 'var_129', 'F', 'V', 'var_129');
INSERT INTO `turbine_model_points` VALUES (1111, '20835', 0, 0, 0, 0, '3#叶片后备电源温度', 'var_128', 'F', '°C', 'var_128');
INSERT INTO `turbine_model_points` VALUES (1112, '20835', 0, 0, 0, 0, '2#叶片后备电源温度', 'var_127', 'F', '°C', 'var_127');
INSERT INTO `turbine_model_points` VALUES (1113, '20835', 0, 0, 0, 0, '1#叶片后备电源温度', 'var_126', 'F', '°C', 'var_126');
INSERT INTO `turbine_model_points` VALUES (1114, '20835', 0, 0, 0, 0, '塔基控制柜温度', 'var_425', 'F', '°C', 'var_425');
INSERT INTO `turbine_model_points` VALUES (1115, '20835', 1, 0, 0, 0, '偏航压力', 'var_412', 'F', 'bar', 'var_412');
INSERT INTO `turbine_model_points` VALUES (1116, '20835', 0, 0, 0, 0, '解缆角度', 'var_410', 'F', '°', 'var_410');
INSERT INTO `turbine_model_points` VALUES (1117, '20835', 1, 1, 1, 0, '偏航角度', 'var_409', 'F', '°', 'var_409');
INSERT INTO `turbine_model_points` VALUES (1118, '20835', 1, 0, 0, 0, '偏航速度', 'var_407', 'F', '°/s', 'var_407');
INSERT INTO `turbine_model_points` VALUES (1119, '20835', 0, 0, 0, 0, '机舱控制柜温度', 'var_380', 'F', '°C', 'var_380');
INSERT INTO `turbine_model_points` VALUES (1120, '20835', 1, 0, 1, 0, '机舱温度', 'var_372', 'F', '°C', 'var_372');
INSERT INTO `turbine_model_points` VALUES (1121, '20835', 1, 0, 1, 0, '环境温度', 'evnTemp', 'F', '°C', 'evnTemp');
INSERT INTO `turbine_model_points` VALUES (1122, '20835', 0, 0, 0, 0, '瞬时风向', 'var_363', 'F', '°', 'var_363');
INSERT INTO `turbine_model_points` VALUES (1123, '20835', 0, 0, 0, 0, '10min平均风速', 'var_359', 'F', 'm/s', 'var_359');
INSERT INTO `turbine_model_points` VALUES (1124, '20835', 1, 1, 1, 0, '2#风速计瞬时风速', 'var_356', 'F', 'm/s', 'var_356');
INSERT INTO `turbine_model_points` VALUES (1125, '20835', 1, 1, 1, 0, '1#风速计瞬时风速', 'var_355', 'F', 'm/s', 'var_355');
INSERT INTO `turbine_model_points` VALUES (1126, '20835', 0, 0, 0, 0, '瞬时风速', 'winSpd', 'F', 'm/s', 'winSpd');
INSERT INTO `turbine_model_points` VALUES (1127, '20835', 0, 0, 0, 0, '电网C相电流', 'var_266', 'F', 'A', 'var_266');
INSERT INTO `turbine_model_points` VALUES (1128, '20835', 0, 0, 0, 0, '电网B相电流', 'var_265', 'F', 'A', 'var_265');
INSERT INTO `turbine_model_points` VALUES (1129, '20835', 0, 0, 0, 0, '电网A相电流', 'var_264', 'F', 'A', 'var_264');
INSERT INTO `turbine_model_points` VALUES (1130, '20835', 0, 0, 0, 0, '电网C相电压', 'var_263', 'F', 'V', 'var_263');
INSERT INTO `turbine_model_points` VALUES (1131, '20835', 0, 0, 0, 0, '电网B相电压', 'var_262', 'F', 'V', 'var_262');
INSERT INTO `turbine_model_points` VALUES (1132, '20835', 0, 0, 0, 0, '电网A相电压', 'var_261', 'F', 'V', 'var_261');
INSERT INTO `turbine_model_points` VALUES (1133, '20835', 0, 0, 0, 0, '电网频率', 'var_257', 'F', 'hz', 'var_257');
INSERT INTO `turbine_model_points` VALUES (1134, '20835', 1, 0, 0, 0, '发电机后轴承温度', 'var_223', 'F', '°C', 'var_223');
INSERT INTO `turbine_model_points` VALUES (1135, '20835', 1, 0, 0, 0, '发电机前轴承温度', 'var_222', 'F', '°C', 'var_222');
INSERT INTO `turbine_model_points` VALUES (1136, '20835', 0, 0, 0, 0, '发电机冷却水温度', 'var_213', 'F', '°C', 'var_213');
INSERT INTO `turbine_model_points` VALUES (1137, '20835', 1, 0, 0, 0, '发电机绕组w2温度', 'var_211', 'F', '°C', 'var_211');
INSERT INTO `turbine_model_points` VALUES (1138, '20835', 1, 0, 0, 0, '发电机绕组w1温度', 'var_210', 'F', '°C', 'var_210');
INSERT INTO `turbine_model_points` VALUES (1139, '20835', 1, 0, 0, 0, '发电机绕组v2温度', 'var_209', 'F', '°C', 'var_209');
INSERT INTO `turbine_model_points` VALUES (1140, '20835', 1, 0, 0, 0, '发电机绕组v1温度', 'var_208', 'F', '°C', 'var_208');
INSERT INTO `turbine_model_points` VALUES (1141, '20835', 1, 0, 0, 0, '发电机绕组u2温度', 'var_207', 'F', '°C', 'var_207');
INSERT INTO `turbine_model_points` VALUES (1142, '20835', 1, 0, 0, 0, '发电机绕组u1温度', 'var_206', 'F', '°C', 'var_206');
INSERT INTO `turbine_model_points` VALUES (1143, '20835', 0, 0, 0, 0, '发电机转速', 'genSpeed', 'F', 'rpm', 'genSpeed');
INSERT INTO `turbine_model_points` VALUES (1144, '20835', 0, 0, 0, 0, '齿轮箱油泵出口压力', 'var_183', 'F', 'Bar', 'var_183');
INSERT INTO `turbine_model_points` VALUES (1145, '20835', 1, 0, 0, 0, '齿轮箱进口压力', 'var_182', 'F', 'Bar', 'var_182');
INSERT INTO `turbine_model_points` VALUES (1146, '20835', 0, 0, 0, 0, '齿轮箱进口油温', 'var_176', 'F', '°C', 'var_176');
INSERT INTO `turbine_model_points` VALUES (1147, '20835', 1, 0, 0, 0, '齿轮箱油池温度', 'var_175', 'F', '°C', 'var_175');
INSERT INTO `turbine_model_points` VALUES (1148, '20835', 0, 0, 0, 0, '主轴温度2', 'var_174', 'F', '°C', 'var_174');
INSERT INTO `turbine_model_points` VALUES (1149, '20835', 0, 0, 0, 0, '主轴温度1', 'var_173', 'F', '°C', 'var_173');
INSERT INTO `turbine_model_points` VALUES (1150, '20835', 1, 0, 0, 0, '齿轮箱HS2轴承温度', 'var_172', 'F', '°C', 'var_172');
INSERT INTO `turbine_model_points` VALUES (1151, '20835', 1, 0, 0, 0, '齿轮箱HS1轴承温度', 'var_171', 'F', '°C', 'var_171');
INSERT INTO `turbine_model_points` VALUES (1152, '20835', 1, 1, 1, 0, '3#叶片实际角度', 'var_103', 'F', '°', 'var_103');
INSERT INTO `turbine_model_points` VALUES (1153, '20835', 1, 1, 1, 0, '2#叶片实际角度', 'var_102', 'F', '°', 'var_102');
INSERT INTO `turbine_model_points` VALUES (1154, '20835', 1, 1, 1, 0, '1#叶片实际角度', 'var_101', 'F', '°', 'var_101');
INSERT INTO `turbine_model_points` VALUES (1155, '20835', 0, 0, 0, 0, '轮毂温度', 'var_1004', 'F', '°C', 'var_1004');
INSERT INTO `turbine_model_points` VALUES (1156, '20835', 1, 0, 1, 0, '风轮转速', 'var_94', 'F', 'RPM', 'var_94');
INSERT INTO `turbine_model_points` VALUES (1157, '20835', 0, 0, 0, 0, '有功功率变化速度反馈值', 'var_63', 'F', 'kW/s', 'var_63');
INSERT INTO `turbine_model_points` VALUES (1158, '20835', 0, 0, 0, 0, '有功功率变化速度', 'var_62', 'F', 'kW/s', 'var_62');
INSERT INTO `turbine_model_points` VALUES (1159, '20835', 0, 0, 0, 0, '功率因数设定反馈值', 'var_55', 'F', 'notdefined', 'var_55');
INSERT INTO `turbine_model_points` VALUES (1160, '20835', 0, 0, 0, 0, '功率因数设定', 'var_54', 'F', 'notdefined', 'var_54');
INSERT INTO `turbine_model_points` VALUES (1161, '20835', 0, 0, 0, 0, '无功功率最大设定反馈值', 'var_53', 'F', 'kVar', 'var_53');
INSERT INTO `turbine_model_points` VALUES (1162, '20835', 0, 0, 0, 0, '有功功率最大设定反馈值', 'var_51', 'F', 'kW', 'var_51');
INSERT INTO `turbine_model_points` VALUES (1163, '20835', 1, 0, 0, 0, '无功功率', 'powReact', 'F', 'kVar', 'powReact');
INSERT INTO `turbine_model_points` VALUES (1164, '20835', 1, 0, 0, 0, '有功功率', 'powAct', 'F', 'kW', 'powAct');
INSERT INTO `turbine_model_points` VALUES (1165, '20835', 0, 0, 0, 0, '机组出口600s平均有功功率', 'var_41', 'F', 'kW', 'var_41');
INSERT INTO `turbine_model_points` VALUES (1166, '20835', 0, 0, 0, 0, '机组变频器出口600s平均有功功率', 'var_203', 'F', 'kW', 'var_203');
INSERT INTO `turbine_model_points` VALUES (1167, '20835', 1, 0, 1, 0, '电网有功功率', 'var_246', 'F', 'kW', 'var_246');
INSERT INTO `turbine_model_points` VALUES (1168, '20835', 0, 0, 0, 0, '日耗电量', 'var_18', 'F', 'kWh', 'var_18');
INSERT INTO `turbine_model_points` VALUES (1169, '20835', 0, 0, 0, 0, '总耗电量', 'totalConsumeEnergy', 'F', 'kWh', 'totalConsumeEnergy');
INSERT INTO `turbine_model_points` VALUES (1170, '20835', 0, 0, 0, 0, '日发电量', 'dayEnergy', 'F', 'kWh', 'dayEnergy');
INSERT INTO `turbine_model_points` VALUES (1171, '20835', 1, 0, 0, 0, '总发电量', 'totalEnergy', 'F', 'kWh', 'totalEnergy');
INSERT INTO `turbine_model_points` VALUES (1172, '20835', 0, 0, 0, 0, '有效风小时数', 'hourWindAva', 'F', 'h', 'hourWindAva');
INSERT INTO `turbine_model_points` VALUES (1173, '20835', 0, 0, 0, 0, '风机自身故障停机时间', 'hourStopFaultOwn', 'F', 'h', 'hourStopFaultOwn');
INSERT INTO `turbine_model_points` VALUES (1174, '20835', 0, 0, 0, 0, '无功功率最大设定值', 'var_52', 'F', 'kVar', 'var_52');
INSERT INTO `turbine_model_points` VALUES (1175, '20835', 0, 0, 0, 0, '故障停机时间', 'hourStopFault', 'F', 'h', 'hourStopFault');
INSERT INTO `turbine_model_points` VALUES (1176, '20835', 0, 0, 0, 0, '服务时间', 'hourMain', 'F', 'h', 'hourMain');
INSERT INTO `turbine_model_points` VALUES (1177, '20835', 1, 0, 0, 0, '发电时间', 'hourGen', 'F', 'h', 'hourGen');
INSERT INTO `turbine_model_points` VALUES (1178, '20835', 0, 0, 0, 0, '电网正常运行时间', 'var_6', 'F', 'h', 'var_6');
INSERT INTO `turbine_model_points` VALUES (1179, '20835', 0, 0, 0, 0, '风机正常运行时间', 'hourTurbNormal', 'F', 'h', 'hourTurbNormal');
INSERT INTO `turbine_model_points` VALUES (1180, '20835', 0, 0, 0, 0, '风暴停机时间', 'hourStopStorm', 'F', 'h', 'hourStopStorm');
INSERT INTO `turbine_model_points` VALUES (1181, '20835', 0, 0, 0, 0, '环境温度过低停机时间', 'hourTempLow', 'F', 'h', 'hourTempLow');
INSERT INTO `turbine_model_points` VALUES (1182, '20835', 0, 0, 0, 0, '人工停机时间', 'hourManualStop', 'F', 'h', 'hourManualStop');
INSERT INTO `turbine_model_points` VALUES (1183, '20835', 0, 0, 0, 0, '运行时间', 'var_1', 'F', 'h', 'var_1');
INSERT INTO `turbine_model_points` VALUES (1184, '20835', 0, 0, 0, 0, '变桨系统充电器故障代码', 'var_15051', 'I', 'notdefined', 'var_15051');
INSERT INTO `turbine_model_points` VALUES (1185, '20835', 0, 0, 0, 0, '2#叶片后备电源容量', 'var_15027', 'F', 'F', 'var_15027');
INSERT INTO `turbine_model_points` VALUES (1186, '20835', 0, 0, 0, 0, '机舱指北30s平均风向SCADA下发值', 'var_18352', 'F', '°', 'var_18352');
INSERT INTO `turbine_model_points` VALUES (1187, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器故障代码', 'var_15049', 'I', 'notdefined', 'var_15049');
INSERT INTO `turbine_model_points` VALUES (1188, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器故障代码', 'var_15050', 'I', 'notdefined', 'var_15050');
INSERT INTO `turbine_model_points` VALUES (1189, '20835', 0, 0, 0, 0, 'HVRT激活', 'var_25000', 'B', 'notdefined', 'var_25000');
INSERT INTO `turbine_model_points` VALUES (1190, '20835', 0, 0, 0, 0, 'LVRT激活', 'var_25001', 'B', 'notdefined', 'var_25001');
INSERT INTO `turbine_model_points` VALUES (1191, '20835', 0, 0, 0, 0, '箱变压力释放阀故障', 'var_30000', 'B', 'notdefined', 'var_30000');
INSERT INTO `turbine_model_points` VALUES (1192, '20835', 0, 0, 0, 0, '变流器警告', 'var_30076', 'B', 'notdefined', 'var_30076');
INSERT INTO `turbine_model_points` VALUES (1193, '20835', 0, 0, 0, 0, '齿轮箱油加热过载警告', 'var_32210', 'B', 'notdefined', 'var_32210');
INSERT INTO `turbine_model_points` VALUES (1194, '20835', 0, 0, 0, 0, '偏航变频器未准备好故障', 'var_32229', 'B', 'notdefined', 'var_32229');
INSERT INTO `turbine_model_points` VALUES (1195, '20835', 0, 0, 0, 0, '变频器1加热请求警告', 'var_35000', 'B', 'notdefined', 'var_35000');
INSERT INTO `turbine_model_points` VALUES (1196, '20835', 0, 0, 0, 0, '变频器2加热请求警告', 'var_35001', 'B', 'notdefined', 'var_35001');
INSERT INTO `turbine_model_points` VALUES (1197, '20835', 0, 0, 0, 0, '变量的值超出其规定范围警告', 'var_35002', 'B', 'notdefined', 'var_35002');
INSERT INTO `turbine_model_points` VALUES (1198, '20835', 0, 0, 0, 0, '本地模式气象站1警告', 'var_35003', 'B', 'notdefined', 'var_35003');
INSERT INTO `turbine_model_points` VALUES (1199, '20835', 0, 0, 0, 0, '本地模式气象站2警告', 'var_35004', 'B', 'notdefined', 'var_35004');
INSERT INTO `turbine_model_points` VALUES (1200, '20835', 0, 0, 0, 0, '远程模式气象站1警告', 'var_35005', 'B', 'notdefined', 'var_35005');
INSERT INTO `turbine_model_points` VALUES (1201, '20835', 0, 0, 0, 0, '远程模式气象站2警告', 'var_35006', 'B', 'notdefined', 'var_35006');
INSERT INTO `turbine_model_points` VALUES (1202, '20835', 0, 0, 0, 0, 'A30柜消防系统压力低警告', 'var_35007', 'B', 'notdefined', 'var_35007');
INSERT INTO `turbine_model_points` VALUES (1203, '20835', 0, 0, 0, 0, '变桨1#叶片驱动器散热片温度故障', 'var_35008', 'B', 'notdefined', 'var_35008');
INSERT INTO `turbine_model_points` VALUES (1204, '20835', 0, 0, 0, 0, '机舱指北30s平均风向', 'winDirAvg30s', 'F', '°', 'winDirAvg30s');
INSERT INTO `turbine_model_points` VALUES (1205, '20835', 0, 0, 0, 0, 'IGBT模块温度', 'var_15041', 'F', '°C', 'var_15041');
INSERT INTO `turbine_model_points` VALUES (1206, '20835', 0, 0, 0, 0, '2#叶片变桨电机转矩', 'var_15039', 'F', 'Nm', 'var_15039');
INSERT INTO `turbine_model_points` VALUES (1207, '20835', 0, 0, 0, 0, '3#叶片驱动器散热片温度', 'var_15037', 'F', '°C', 'var_15037');
INSERT INTO `turbine_model_points` VALUES (1208, '20835', 0, 0, 0, 0, '2#叶片驱动器散热片温度', 'var_15036', 'F', '°C', 'var_15036');
INSERT INTO `turbine_model_points` VALUES (1209, '20835', 0, 0, 0, 0, '1#叶片驱动器散热片温度', 'var_15035', 'F', '°C', 'var_15035');
INSERT INTO `turbine_model_points` VALUES (1210, '20835', 0, 0, 0, 0, '3#叶片驱动器控制板温度', 'var_15034', 'F', '°C', 'var_15034');
INSERT INTO `turbine_model_points` VALUES (1211, '20835', 0, 0, 0, 0, '2#叶片驱动器控制板温度', 'var_15033', 'F', '°C', 'var_15033');
INSERT INTO `turbine_model_points` VALUES (1212, '20835', 0, 0, 0, 0, '1#叶片驱动器控制板温度', 'var_15032', 'F', '°C', 'var_15032');
INSERT INTO `turbine_model_points` VALUES (1213, '20835', 0, 0, 0, 0, '3#叶片后备电源内阻', 'var_15031', 'F', 'mΩ', 'var_15031');
INSERT INTO `turbine_model_points` VALUES (1214, '20835', 0, 0, 0, 0, '2#叶片后备电源内阻', 'var_15030', 'F', 'mOhm', 'var_15030');
INSERT INTO `turbine_model_points` VALUES (1215, '20835', 0, 0, 0, 0, '1#叶片后备电源内阻', 'var_15029', 'F', 'mΩ', 'var_15029');
INSERT INTO `turbine_model_points` VALUES (1216, '20835', 0, 0, 0, 0, '3#叶片后备电源容量', 'var_15028', 'F', 'F', 'var_15028');
INSERT INTO `turbine_model_points` VALUES (1217, '20835', 0, 0, 0, 0, '1#叶片后备电源容量', 'var_15026', 'F', 'F', 'var_15026');
INSERT INTO `turbine_model_points` VALUES (1218, '20835', 0, 0, 0, 0, '3#叶片Z方向加速度', 'var_15025', 'F', 'g', 'var_15025');
INSERT INTO `turbine_model_points` VALUES (1219, '20835', 0, 0, 0, 0, '2#叶片Z方向加速度', 'var_15024', 'F', 'g', 'var_15024');
INSERT INTO `turbine_model_points` VALUES (1220, '20835', 0, 0, 0, 0, '1#叶片Z方向加速度', 'var_15023', 'F', 'g', 'var_15023');
INSERT INTO `turbine_model_points` VALUES (1221, '20835', 0, 0, 0, 0, '3#叶片Y方向加速度', 'var_15022', 'F', 'g', 'var_15022');
INSERT INTO `turbine_model_points` VALUES (1222, '20835', 0, 0, 0, 0, '2#叶片Y方向加速度', 'var_15021', 'F', 'g', 'var_15021');
INSERT INTO `turbine_model_points` VALUES (1223, '20835', 0, 0, 0, 0, '1#叶片Y方向加速度', 'var_15020', 'F', 'g', 'var_15020');
INSERT INTO `turbine_model_points` VALUES (1224, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器散热片温度故障', 'var_35009', 'B', 'notdefined', 'var_35009');
INSERT INTO `turbine_model_points` VALUES (1225, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器散热片温度故障', 'var_35010', 'B', 'notdefined', 'var_35010');
INSERT INTO `turbine_model_points` VALUES (1226, '20835', 0, 0, 0, 0, '变桨1#叶片电源1温度故障', 'var_35011', 'B', 'notdefined', 'var_35011');
INSERT INTO `turbine_model_points` VALUES (1227, '20835', 0, 0, 0, 0, '变桨2#叶片电源1温度故障', 'var_35012', 'B', 'notdefined', 'var_35012');
INSERT INTO `turbine_model_points` VALUES (1228, '20835', 0, 0, 0, 0, '变桨3#叶片电源1温度故障', 'var_35013', 'B', 'notdefined', 'var_35013');
INSERT INTO `turbine_model_points` VALUES (1229, '20835', 0, 0, 0, 0, '变桨1#叶片驱动器控制板温度故障', 'var_35014', 'B', 'notdefined', 'var_35014');
INSERT INTO `turbine_model_points` VALUES (1230, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器控制板温度故障', 'var_35015', 'B', 'notdefined', 'var_35015');
INSERT INTO `turbine_model_points` VALUES (1231, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器控制板温度故障', 'var_35016', 'B', 'notdefined', 'var_35016');
INSERT INTO `turbine_model_points` VALUES (1232, '20835', 0, 0, 0, 0, '变桨系统一般故障', 'var_35017', 'B', 'notdefined', 'var_35017');
INSERT INTO `turbine_model_points` VALUES (1233, '20835', 0, 0, 0, 0, '变桨系统控制器故障', 'var_35018', 'B', 'notdefined', 'var_35018');
INSERT INTO `turbine_model_points` VALUES (1234, '20835', 0, 0, 0, 0, '变桨1#叶片驱动器Ethernet通讯故障', 'var_35019', 'B', 'notdefined', 'var_35019');
INSERT INTO `turbine_model_points` VALUES (1235, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器Ethernet通讯故障', 'var_35020', 'B', 'notdefined', 'var_35020');
INSERT INTO `turbine_model_points` VALUES (1236, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器Ethernet通讯故障', 'var_35021', 'B', 'notdefined', 'var_35021');
INSERT INTO `turbine_model_points` VALUES (1237, '20835', 0, 0, 0, 0, '变桨1#叶片电机风扇断路器分闸警告', 'var_35022', 'B', 'notdefined', 'var_35022');
INSERT INTO `turbine_model_points` VALUES (1238, '20835', 0, 0, 0, 0, '变桨2#叶片电机风扇断路器分闸警告', 'var_35023', 'B', 'notdefined', 'var_35023');
INSERT INTO `turbine_model_points` VALUES (1239, '20835', 0, 0, 0, 0, '变桨3#叶片电机风扇断路器分闸警告', 'var_35024', 'B', 'notdefined', 'var_35024');
INSERT INTO `turbine_model_points` VALUES (1240, '20835', 0, 0, 0, 0, '变桨1#叶片电机编码器故障', 'var_35025', 'B', 'notdefined', 'var_35025');
INSERT INTO `turbine_model_points` VALUES (1241, '20835', 0, 0, 0, 0, '变桨2#叶片电机编码器故障', 'var_35026', 'B', 'notdefined', 'var_35026');
INSERT INTO `turbine_model_points` VALUES (1242, '20835', 0, 0, 0, 0, '变桨3#叶片电机编码器故障', 'var_35027', 'B', 'notdefined', 'var_35027');
INSERT INTO `turbine_model_points` VALUES (1243, '20835', 0, 0, 0, 0, '变桨1#叶片备用24V电源故障', 'var_35028', 'B', 'notdefined', 'var_35028');
INSERT INTO `turbine_model_points` VALUES (1244, '20835', 0, 0, 0, 0, '变桨2#叶片备用24V电源故障', 'var_35029', 'B', 'notdefined', 'var_35029');
INSERT INTO `turbine_model_points` VALUES (1245, '20835', 0, 0, 0, 0, '变桨3#叶片备用24V电源故障', 'var_35030', 'B', 'notdefined', 'var_35030');
INSERT INTO `turbine_model_points` VALUES (1246, '20835', 0, 0, 0, 0, '变桨1#叶片后备电源连接故障', 'var_35031', 'B', 'notdefined', 'var_35031');
INSERT INTO `turbine_model_points` VALUES (1247, '20835', 0, 0, 0, 0, '变桨2#叶片后备电源连接故障', 'var_35032', 'B', 'notdefined', 'var_35032');
INSERT INTO `turbine_model_points` VALUES (1248, '20835', 0, 0, 0, 0, '变桨3#叶片后备电源连接故障', 'var_35033', 'B', 'notdefined', 'var_35033');
INSERT INTO `turbine_model_points` VALUES (1249, '20835', 0, 0, 0, 0, '变桨系统供电电源防雷警告', 'var_35034', 'B', 'notdefined', 'var_35034');
INSERT INTO `turbine_model_points` VALUES (1250, '20835', 0, 0, 0, 0, '变桨系统重载插头连接警告', 'var_35035', 'B', 'notdefined', 'var_35035');
INSERT INTO `turbine_model_points` VALUES (1251, '20835', 0, 0, 0, 0, '变桨1#叶片电源故障', 'var_35036', 'B', 'notdefined', 'var_35036');
INSERT INTO `turbine_model_points` VALUES (1252, '20835', 0, 0, 0, 0, '变桨2#叶片电源故障', 'var_35037', 'B', 'notdefined', 'var_35037');
INSERT INTO `turbine_model_points` VALUES (1253, '20835', 0, 0, 0, 0, '变桨3#叶片电源故障', 'var_35038', 'B', 'notdefined', 'var_35038');
INSERT INTO `turbine_model_points` VALUES (1254, '20835', 0, 0, 0, 0, '变桨1#叶片一般故障', 'var_35039', 'B', 'notdefined', 'var_35039');
INSERT INTO `turbine_model_points` VALUES (1255, '20835', 0, 0, 0, 0, '变桨2#叶片一般故障', 'var_35040', 'B', 'notdefined', 'var_35040');
INSERT INTO `turbine_model_points` VALUES (1256, '20835', 0, 0, 0, 0, '变桨3#叶片一般故障', 'var_35041', 'B', 'notdefined', 'var_35041');
INSERT INTO `turbine_model_points` VALUES (1257, '20835', 0, 0, 0, 0, '变桨1#叶片严重故障', 'var_35042', 'B', 'notdefined', 'var_35042');
INSERT INTO `turbine_model_points` VALUES (1258, '20835', 0, 0, 0, 0, '变桨2#叶片严重故障', 'var_35043', 'B', 'notdefined', 'var_35043');
INSERT INTO `turbine_model_points` VALUES (1259, '20835', 0, 0, 0, 0, '变桨3#叶片严重故障', 'var_35044', 'B', 'notdefined', 'var_35044');
INSERT INTO `turbine_model_points` VALUES (1260, '20835', 0, 0, 0, 0, '变桨系统控制器Ethernet通讯故障', 'var_35045', 'B', 'notdefined', 'var_35045');
INSERT INTO `turbine_model_points` VALUES (1261, '20835', 0, 0, 0, 0, '变桨系统PPI内部CAN通讯故障', 'var_35046', 'B', 'notdefined', 'var_35046');
INSERT INTO `turbine_model_points` VALUES (1262, '20835', 0, 0, 0, 0, '变桨供电电源故障', 'var_35047', 'B', 'notdefined', 'var_35047');
INSERT INTO `turbine_model_points` VALUES (1263, '20835', 0, 0, 0, 0, '变桨1#叶片电机刹车电源故障', 'var_35048', 'B', 'notdefined', 'var_35048');
INSERT INTO `turbine_model_points` VALUES (1264, '20835', 0, 0, 0, 0, '变桨2#叶片电机刹车电源故障', 'var_35049', 'B', 'notdefined', 'var_35049');
INSERT INTO `turbine_model_points` VALUES (1265, '20835', 0, 0, 0, 0, '变桨3#叶片电机刹车电源故障', 'var_35050', 'B', 'notdefined', 'var_35050');
INSERT INTO `turbine_model_points` VALUES (1266, '20835', 0, 0, 0, 0, '变桨系统润滑泵供电电源故障', 'var_35051', 'B', 'notdefined', 'var_35051');
INSERT INTO `turbine_model_points` VALUES (1267, '20835', 0, 0, 0, 0, '变桨1#叶片驱动器EFC激活故障', 'var_35052', 'B', 'notdefined', 'var_35052');
INSERT INTO `turbine_model_points` VALUES (1268, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器EFC激活故障', 'var_35053', 'B', 'notdefined', 'var_35053');
INSERT INTO `turbine_model_points` VALUES (1269, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器EFC激活故障', 'var_35054', 'B', 'notdefined', 'var_35054');
INSERT INTO `turbine_model_points` VALUES (1270, '20835', 0, 0, 0, 0, '变桨1#叶片驱动器软件EFC激活故障', 'var_35055', 'B', 'notdefined', 'var_35055');
INSERT INTO `turbine_model_points` VALUES (1271, '20835', 0, 0, 0, 0, '变桨2#叶片驱动器软件EFC激活故障', 'var_35056', 'B', 'notdefined', 'var_35056');
INSERT INTO `turbine_model_points` VALUES (1272, '20835', 0, 0, 0, 0, '变桨3#叶片驱动器软件EFC激活故障', 'var_35057', 'B', 'notdefined', 'var_35057');
INSERT INTO `turbine_model_points` VALUES (1273, '20835', 0, 0, 0, 0, '变流器MCB跳闸', 'var_35058', 'B', 'notdefined', 'var_35058');
INSERT INTO `turbine_model_points` VALUES (1274, '20835', 0, 0, 0, 0, '变流器1警告', 'var_35061', 'B', 'notdefined', 'var_35061');
INSERT INTO `turbine_model_points` VALUES (1275, '20835', 0, 0, 0, 0, '变流器2警告', 'var_35062', 'B', 'notdefined', 'var_35062');
INSERT INTO `turbine_model_points` VALUES (1276, '20835', 0, 0, 0, 0, '机舱控制柜消防报警1级故障', 'var_35065', 'B', 'notdefined', 'var_35065');
INSERT INTO `turbine_model_points` VALUES (1277, '20835', 0, 0, 0, 0, '机舱控制柜消防报警2级故障', 'var_35066', 'B', 'notdefined', 'var_35066');
INSERT INTO `turbine_model_points` VALUES (1278, '20835', 0, 0, 0, 0, '雷电监测系统电源警告', 'var_35067', 'B', 'notdefined', 'var_35067');
INSERT INTO `turbine_model_points` VALUES (1279, '20835', 0, 0, 0, 0, '雷电监测系统警告', 'var_35068', 'B', 'notdefined', 'var_35068');
INSERT INTO `turbine_model_points` VALUES (1280, '20835', 0, 0, 0, 0, '电缆温度高故障', 'var_35069', 'B', 'notdefined', 'var_35069');
INSERT INTO `turbine_model_points` VALUES (1281, '20835', 0, 0, 0, 0, '箱变温控器传感器故障', 'var_35071', 'B', 'notdefined', 'var_35071');
INSERT INTO `turbine_model_points` VALUES (1282, '20835', 0, 0, 0, 0, '机舱除湿机滤网堵塞警告', 'var_35072', 'B', 'notdefined', 'var_35072');
INSERT INTO `turbine_model_points` VALUES (1283, '20835', 0, 0, 0, 0, '塔基除湿机滤网堵塞警告', 'var_35073', 'B', 'notdefined', 'var_35073');
INSERT INTO `turbine_model_points` VALUES (1284, '20835', 0, 0, 0, 0, '偏航变频器通讯错误', 'var_35074', 'B', 'notdefined', 'var_35074');
INSERT INTO `turbine_model_points` VALUES (1285, '20835', 0, 0, 0, 0, '机舱偏航未移动', 'var_35075', 'B', 'notdefined', 'var_35075');
INSERT INTO `turbine_model_points` VALUES (1286, '20835', 0, 0, 0, 0, '齿轮箱轴承温差大警告', 'var_35076', 'B', 'notdefined', 'var_35076');
INSERT INTO `turbine_model_points` VALUES (1287, '20835', 0, 0, 0, 0, '齿轮箱旁路过滤电机过载', 'var_35077', 'B', 'notdefined', 'var_35077');
INSERT INTO `turbine_model_points` VALUES (1288, '20835', 0, 0, 0, 0, '发电机润滑故障', 'var_35078', 'B', 'notdefined', 'var_35078');
INSERT INTO `turbine_model_points` VALUES (1289, '20835', 0, 0, 0, 0, '机舱外部冷却风扇1过载警告2', 'var_35079', 'B', 'notdefined', 'var_35079');
INSERT INTO `turbine_model_points` VALUES (1290, '20835', 0, 0, 0, 0, '机舱外部冷却风扇2过载警告2', 'var_35080', 'B', 'notdefined', 'var_35080');
INSERT INTO `turbine_model_points` VALUES (1291, '20835', 0, 0, 0, 0, '箱变集控装置电源掉电故障', 'var_35081', 'B', 'notdefined', 'var_35081');
INSERT INTO `turbine_model_points` VALUES (1292, '20835', 0, 0, 0, 0, 'A11控制柜温度1（中）高警告', 'var_35083', 'B', 'notdefined', 'var_35083');
INSERT INTO `turbine_model_points` VALUES (1293, '20835', 0, 0, 0, 0, 'A11控制柜温度1（中）低警告', 'var_35084', 'B', 'notdefined', 'var_35084');
INSERT INTO `turbine_model_points` VALUES (1294, '20835', 0, 0, 0, 0, 'A11控制柜温度1（中）太高故障', 'var_35085', 'B', 'notdefined', 'var_35085');
INSERT INTO `turbine_model_points` VALUES (1295, '20835', 0, 0, 0, 0, 'A11控制柜温度1（中）太低故障', 'var_35086', 'B', 'notdefined', 'var_35086');
INSERT INTO `turbine_model_points` VALUES (1296, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片后备电源电压高故障', 'var_35087', 'B', 'notdefined', 'var_35087');
INSERT INTO `turbine_model_points` VALUES (1297, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片后备电源电压高故障', 'var_35088', 'B', 'notdefined', 'var_35088');
INSERT INTO `turbine_model_points` VALUES (1298, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片后备电源电压高故障', 'var_35089', 'B', 'notdefined', 'var_35089');
INSERT INTO `turbine_model_points` VALUES (1299, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片限位开关1误触发故障', 'var_35090', 'B', 'notdefined', 'var_35090');
INSERT INTO `turbine_model_points` VALUES (1300, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片限位开关1误触发故障', 'var_35091', 'B', 'notdefined', 'var_35091');
INSERT INTO `turbine_model_points` VALUES (1301, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片限位开关1误触发故障', 'var_35092', 'B', 'notdefined', 'var_35092');
INSERT INTO `turbine_model_points` VALUES (1302, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片限位开关1误触发故障', 'var_35093', 'B', 'notdefined', 'var_35093');
INSERT INTO `turbine_model_points` VALUES (1303, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片限位开关2误触发故障', 'var_35094', 'B', 'notdefined', 'var_35094');
INSERT INTO `turbine_model_points` VALUES (1304, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片限位开关3误触发故障', 'var_35095', 'B', 'notdefined', 'var_35095');
INSERT INTO `turbine_model_points` VALUES (1305, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片后备电源需更换故障', 'var_35096', 'B', 'notdefined', 'var_35096');
INSERT INTO `turbine_model_points` VALUES (1306, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片后备电源需更换故障', 'var_35097', 'B', 'notdefined', 'var_35097');
INSERT INTO `turbine_model_points` VALUES (1307, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片后备电源需更换故障', 'var_35098', 'B', 'notdefined', 'var_35098');
INSERT INTO `turbine_model_points` VALUES (1308, '20835', 0, 0, 0, 0, '变桨系统检测1#叶片软启单元故障', 'var_35099', 'B', 'notdefined', 'var_35099');
INSERT INTO `turbine_model_points` VALUES (1309, '20835', 0, 0, 0, 0, '变桨系统检测2#叶片软启单元故障', 'var_35100', 'B', 'notdefined', 'var_35100');
INSERT INTO `turbine_model_points` VALUES (1310, '20835', 0, 0, 0, 0, '变桨系统检测3#叶片软启单元故障', 'var_35101', 'B', 'notdefined', 'var_35101');
INSERT INTO `turbine_model_points` VALUES (1311, '20835', 0, 0, 0, 0, '箱变气体继电器轻瓦斯警告', 'var_35102', 'B', 'notdefined', 'var_35102');
INSERT INTO `turbine_model_points` VALUES (1312, '20835', 0, 0, 0, 0, '箱变气体继电器重瓦斯跳闸故障', 'var_35103', 'B', 'notdefined', 'var_35103');
INSERT INTO `turbine_model_points` VALUES (1313, '20835', 0, 0, 0, 0, '箱变油位低警告', 'var_35105', 'B', 'notdefined', 'var_35105');
INSERT INTO `turbine_model_points` VALUES (1314, '20835', 0, 0, 0, 0, '箱变压力跳闸故障', 'var_35106', 'B', 'notdefined', 'var_35106');
INSERT INTO `turbine_model_points` VALUES (1315, '20835', 0, 0, 0, 0, '箱变油泵电机过载故障', 'var_35107', 'B', 'notdefined', 'var_35107');
INSERT INTO `turbine_model_points` VALUES (1316, '20835', 0, 0, 0, 0, '箱变油泵超温故障', 'var_35108', 'B', 'notdefined', 'var_35108');
INSERT INTO `turbine_model_points` VALUES (1317, '20835', 0, 0, 0, 0, '塔基应急舱供电过载警告', 'var_35109', 'B', 'notdefined', 'var_35109');
INSERT INTO `turbine_model_points` VALUES (1318, '20835', 0, 0, 0, 0, '环网柜控制电源消失故障', 'var_38361', 'B', 'notdefined', 'var_38361');
INSERT INTO `turbine_model_points` VALUES (1319, '20835', 0, 0, 0, 0, '环网柜继电保护动作故障', 'var_38362', 'B', 'notdefined', 'var_38362');
INSERT INTO `turbine_model_points` VALUES (1320, '20835', 0, 0, 0, 0, '机舱控制柜消防系统动作故障', 'var_38363', 'B', 'notdefined', 'var_38363');
INSERT INTO `turbine_model_points` VALUES (1321, '20835', 0, 0, 0, 0, '变流器消防系统动作故障', 'var_38364', 'B', 'notdefined', 'var_38364');
INSERT INTO `turbine_model_points` VALUES (1322, '20835', 0, 0, 0, 0, '变压器消防系统动作故障', 'var_38365', 'B', 'notdefined', 'var_38365');
INSERT INTO `turbine_model_points` VALUES (1323, '20835', 0, 0, 0, 0, '塔基控制柜消防系统动作故障', 'var_38366', 'B', 'notdefined', 'var_38366');
INSERT INTO `turbine_model_points` VALUES (1324, '20835', 0, 0, 0, 0, '机舱大空间消防系统动作故障', 'var_38367', 'B', 'notdefined', 'var_38367');
INSERT INTO `turbine_model_points` VALUES (1325, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨88°接近开关故障', 'var_38368', 'B', 'notdefined', 'var_38368');
INSERT INTO `turbine_model_points` VALUES (1326, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨88°接近开关故障', 'var_38369', 'B', 'notdefined', 'var_38369');
INSERT INTO `turbine_model_points` VALUES (1327, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨88°接近开关故障', 'var_38370', 'B', 'notdefined', 'var_38370');
INSERT INTO `turbine_model_points` VALUES (1328, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨3°接近开关故障', 'var_38371', 'B', 'notdefined', 'var_38371');
INSERT INTO `turbine_model_points` VALUES (1329, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨3°接近开关故障', 'var_38372', 'B', 'notdefined', 'var_38372');
INSERT INTO `turbine_model_points` VALUES (1330, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨3°接近开关故障', 'var_38373', 'B', 'notdefined', 'var_38373');
INSERT INTO `turbine_model_points` VALUES (1331, '20835', 0, 0, 0, 0, '变桨系统报出低穿超时故障', 'var_38374', 'B', 'notdefined', 'var_38374');
INSERT INTO `turbine_model_points` VALUES (1332, '20835', 0, 0, 0, 0, '变桨系统报出高穿超时故障', 'var_38375', 'B', 'notdefined', 'var_38375');
INSERT INTO `turbine_model_points` VALUES (1333, '20835', 0, 0, 0, 0, '变桨1#叶片报出91°限位开关激活故障', 'var_38376', 'B', 'notdefined', 'var_38376');
INSERT INTO `turbine_model_points` VALUES (1334, '20835', 0, 0, 0, 0, '变桨2#叶片报出91°限位开关激活故障', 'var_38377', 'B', 'notdefined', 'var_38377');
INSERT INTO `turbine_model_points` VALUES (1335, '20835', 0, 0, 0, 0, '变桨3#叶片报出91°限位开关激活故障', 'var_38378', 'B', 'notdefined', 'var_38378');
INSERT INTO `turbine_model_points` VALUES (1336, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨闭环停机超速故障', 'var_38379', 'B', 'notdefined', 'var_38379');
INSERT INTO `turbine_model_points` VALUES (1337, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨闭环停机超速故障', 'var_38380', 'B', 'notdefined', 'var_38380');
INSERT INTO `turbine_model_points` VALUES (1338, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨闭环停机超速故障', 'var_38381', 'B', 'notdefined', 'var_38381');
INSERT INTO `turbine_model_points` VALUES (1339, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨闭环停机超时故障', 'var_38382', 'B', 'notdefined', 'var_38382');
INSERT INTO `turbine_model_points` VALUES (1340, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨闭环停机超时故障', 'var_38383', 'B', 'notdefined', 'var_38383');
INSERT INTO `turbine_model_points` VALUES (1341, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨闭环停机超时故障', 'var_38384', 'B', 'notdefined', 'var_38384');
INSERT INTO `turbine_model_points` VALUES (1342, '20835', 0, 0, 0, 0, '变桨1#叶片检测到变桨网侧24V供电故障', 'var_38385', 'B', 'notdefined', 'var_38385');
INSERT INTO `turbine_model_points` VALUES (1343, '20835', 0, 0, 0, 0, '变桨2#叶片检测到变桨网侧24V供电故障', 'var_38386', 'B', 'notdefined', 'var_38386');
INSERT INTO `turbine_model_points` VALUES (1344, '20835', 0, 0, 0, 0, '变桨3#叶片检测到变桨网侧24V供电故障', 'var_38387', 'B', 'notdefined', 'var_38387');
INSERT INTO `turbine_model_points` VALUES (1345, '20835', 0, 0, 0, 0, '变桨1#叶片检测到变桨软件EFC故障', 'var_38388', 'B', 'notdefined', 'var_38388');
INSERT INTO `turbine_model_points` VALUES (1346, '20835', 0, 0, 0, 0, '变桨2#叶片检测到变桨软件EFC故障', 'var_38389', 'B', 'notdefined', 'var_38389');
INSERT INTO `turbine_model_points` VALUES (1347, '20835', 0, 0, 0, 0, '变桨3#叶片检测到变桨软件EFC故障', 'var_38390', 'B', 'notdefined', 'var_38390');
INSERT INTO `turbine_model_points` VALUES (1348, '20835', 0, 0, 0, 0, '变桨1#叶片检测到变桨电容模块容量太低故障', 'var_38391', 'B', 'notdefined', 'var_38391');
INSERT INTO `turbine_model_points` VALUES (1349, '20835', 0, 0, 0, 0, '变桨2#叶片检测到变桨电容模块容量太低故障', 'var_38392', 'B', 'notdefined', 'var_38392');
INSERT INTO `turbine_model_points` VALUES (1350, '20835', 0, 0, 0, 0, '变桨3#叶片检测到变桨电容模块容量太低故障', 'var_38393', 'B', 'notdefined', 'var_38393');
INSERT INTO `turbine_model_points` VALUES (1351, '20835', 0, 0, 0, 0, '变桨1#叶片检测到变桨驱动器温度过高故障', 'var_38394', 'B', 'notdefined', 'var_38394');
INSERT INTO `turbine_model_points` VALUES (1352, '20835', 0, 0, 0, 0, '变桨2#叶片检测到变桨驱动器温度过高故障', 'var_38395', 'B', 'notdefined', 'var_38395');
INSERT INTO `turbine_model_points` VALUES (1353, '20835', 0, 0, 0, 0, '变桨3#叶片检测到变桨驱动器温度过高故障', 'var_38396', 'B', 'notdefined', 'var_38396');
INSERT INTO `turbine_model_points` VALUES (1354, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨内部CAN通讯故障', 'var_38397', 'B', 'notdefined', 'var_38397');
INSERT INTO `turbine_model_points` VALUES (1355, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨内部CAN通讯故障', 'var_38398', 'B', 'notdefined', 'var_38398');
INSERT INTO `turbine_model_points` VALUES (1356, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨内部CAN通讯故障', 'var_38399', 'B', 'notdefined', 'var_38399');
INSERT INTO `turbine_model_points` VALUES (1357, '20835', 0, 0, 0, 0, '变桨1#叶片报出变桨电容温度太高故障', 'var_38400', 'B', 'notdefined', 'var_38400');
INSERT INTO `turbine_model_points` VALUES (1358, '20835', 0, 0, 0, 0, '变桨2#叶片报出变桨电容温度太高故障', 'var_38401', 'B', 'notdefined', 'var_38401');
INSERT INTO `turbine_model_points` VALUES (1359, '20835', 0, 0, 0, 0, '变桨3#叶片报出变桨电容温度太高故障', 'var_38402', 'B', 'notdefined', 'var_38402');
INSERT INTO `turbine_model_points` VALUES (1360, '20835', 0, 0, 0, 0, '1#叶片变桨电机转子锁定故障', 'var_38403', 'B', 'notdefined', 'var_38403');
INSERT INTO `turbine_model_points` VALUES (1361, '20835', 0, 0, 0, 0, '2#叶片变桨电机转子锁定故障', 'var_38404', 'B', 'notdefined', 'var_38404');
INSERT INTO `turbine_model_points` VALUES (1362, '20835', 0, 0, 0, 0, '3#叶片变桨电机转子锁定故障', 'var_38405', 'B', 'notdefined', 'var_38405');
INSERT INTO `turbine_model_points` VALUES (1363, '20835', 0, 0, 0, 0, '1#叶片变桨供电电压高故障', 'var_38406', 'B', 'notdefined', 'var_38406');
INSERT INTO `turbine_model_points` VALUES (1364, '20835', 0, 0, 0, 0, '2#叶片变桨供电电压高故障', 'var_38407', 'B', 'notdefined', 'var_38407');
INSERT INTO `turbine_model_points` VALUES (1365, '20835', 0, 0, 0, 0, '3#叶片变桨供电电压高故障', 'var_38408', 'B', 'notdefined', 'var_38408');
INSERT INTO `turbine_model_points` VALUES (1366, '20835', 0, 0, 0, 0, '1#叶片变桨电容单体温度高故障', 'var_38409', 'B', 'notdefined', 'var_38409');
INSERT INTO `turbine_model_points` VALUES (1367, '20835', 0, 0, 0, 0, '2#叶片变桨电容单体温度高故障', 'var_38410', 'B', 'notdefined', 'var_38410');
INSERT INTO `turbine_model_points` VALUES (1368, '20835', 0, 0, 0, 0, '3#叶片变桨电容单体温度高故障', 'var_38411', 'B', 'notdefined', 'var_38411');
INSERT INTO `turbine_model_points` VALUES (1369, '20835', 0, 0, 0, 0, '1#叶片变桨电容单体电压高故障', 'var_38412', 'B', 'notdefined', 'var_38412');
INSERT INTO `turbine_model_points` VALUES (1370, '20835', 0, 0, 0, 0, '2#叶片变桨电容单体电压高故障', 'var_38413', 'B', 'notdefined', 'var_38413');
INSERT INTO `turbine_model_points` VALUES (1371, '20835', 0, 0, 0, 0, '3#叶片变桨电容单体电压高故障', 'var_38414', 'B', 'notdefined', 'var_38414');
INSERT INTO `turbine_model_points` VALUES (1372, '20835', 0, 0, 0, 0, '变桨1#叶片检测转子超速故障', 'var_38415', 'B', 'notdefined', 'var_38415');
INSERT INTO `turbine_model_points` VALUES (1373, '20835', 0, 0, 0, 0, '变桨2#叶片检测转子超速故障', 'var_38416', 'B', 'notdefined', 'var_38416');
INSERT INTO `turbine_model_points` VALUES (1374, '20835', 0, 0, 0, 0, '变桨3#叶片检测转子超速故障', 'var_38417', 'B', 'notdefined', 'var_38417');
INSERT INTO `turbine_model_points` VALUES (1375, '20835', 0, 0, 0, 0, '1#叶片制动马达制动失败故障', 'var_38418', 'B', 'notdefined', 'var_38418');
INSERT INTO `turbine_model_points` VALUES (1376, '20835', 0, 0, 0, 0, '2#叶片制动马达制动失败故障', 'var_38419', 'B', 'notdefined', 'var_38419');
INSERT INTO `turbine_model_points` VALUES (1377, '20835', 0, 0, 0, 0, '3#叶片制动马达制动失败故障', 'var_38420', 'B', 'notdefined', 'var_38420');
INSERT INTO `turbine_model_points` VALUES (1378, '20835', 0, 0, 0, 0, '1#叶片低电容或高内阻故障', 'var_38421', 'B', 'notdefined', 'var_38421');
INSERT INTO `turbine_model_points` VALUES (1379, '20835', 0, 0, 0, 0, '2#叶片低电容或高内阻故障', 'var_38422', 'B', 'notdefined', 'var_38422');
INSERT INTO `turbine_model_points` VALUES (1380, '20835', 0, 0, 0, 0, '3#叶片低电容或高内阻故障', 'var_38423', 'B', 'notdefined', 'var_38423');
INSERT INTO `turbine_model_points` VALUES (1381, '20835', 0, 0, 0, 0, '1#叶片变桨无心跳故障', 'var_38424', 'B', 'notdefined', 'var_38424');
INSERT INTO `turbine_model_points` VALUES (1382, '20835', 0, 0, 0, 0, '2#叶片变桨无心跳故障', 'var_38425', 'B', 'notdefined', 'var_38425');
INSERT INTO `turbine_model_points` VALUES (1383, '20835', 0, 0, 0, 0, '3#叶片变桨无心跳故障', 'var_38426', 'B', 'notdefined', 'var_38426');
INSERT INTO `turbine_model_points` VALUES (1384, '20835', 0, 0, 0, 0, '偏航微动开关故障', 'var_38427', 'B', 'notdefined', 'var_38427');
INSERT INTO `turbine_model_points` VALUES (1385, '20835', 0, 0, 0, 0, '风速仪故障', 'var_38428', 'B', 'notdefined', 'var_38428');
INSERT INTO `turbine_model_points` VALUES (1386, '20835', 0, 0, 0, 0, '风向仪故障', 'var_38429', 'B', 'notdefined', 'var_38429');
INSERT INTO `turbine_model_points` VALUES (1387, '20835', 0, 0, 0, 0, '风速1警告', 'var_38430', 'B', 'notdefined', 'var_38430');
INSERT INTO `turbine_model_points` VALUES (1388, '20835', 0, 0, 0, 0, '风速2警告', 'var_38431', 'B', 'notdefined', 'var_38431');
INSERT INTO `turbine_model_points` VALUES (1389, '20835', 0, 0, 0, 0, '风向1警告', 'var_38432', 'B', 'notdefined', 'var_38432');
INSERT INTO `turbine_model_points` VALUES (1390, '20835', 0, 0, 0, 0, '风向2警告', 'var_38433', 'B', 'notdefined', 'var_38433');
INSERT INTO `turbine_model_points` VALUES (1391, '20835', 0, 0, 0, 0, '塔基门开警告', 'var_38434', 'B', 'notdefined', 'var_38434');
INSERT INTO `turbine_model_points` VALUES (1392, '20835', 0, 0, 0, 0, '塔基防雷警告', 'var_38435', 'B', 'notdefined', 'var_38435');
INSERT INTO `turbine_model_points` VALUES (1393, '20835', 0, 0, 0, 0, '后备电源过载警告', 'var_38436', 'B', 'notdefined', 'var_38436');
INSERT INTO `turbine_model_points` VALUES (1394, '20835', 0, 0, 0, 0, '塔基自动消防故障', 'var_38437', 'B', 'notdefined', 'var_38437');
INSERT INTO `turbine_model_points` VALUES (1395, '20835', 0, 0, 0, 0, '辅助供电过载故障', 'var_38438', 'B', 'notdefined', 'var_38438');
INSERT INTO `turbine_model_points` VALUES (1396, '20835', 0, 0, 0, 0, '机舱防雷警告', 'var_38439', 'B', 'notdefined', 'var_38439');
INSERT INTO `turbine_model_points` VALUES (1397, '20835', 0, 0, 0, 0, '机舱自动消防故障', 'var_38440', 'B', 'notdefined', 'var_38440');
INSERT INTO `turbine_model_points` VALUES (1398, '20835', 0, 0, 0, 0, '机舱SOS', 'var_38441', 'B', 'notdefined', 'var_38441');
INSERT INTO `turbine_model_points` VALUES (1399, '20835', 0, 0, 0, 0, '主轴后轴承1温度高故障', 'var_38442', 'B', 'notdefined', 'var_38442');
INSERT INTO `turbine_model_points` VALUES (1400, '20835', 0, 0, 0, 0, '主轴后轴承2温度高故障', 'var_38443', 'B', 'notdefined', 'var_38443');
INSERT INTO `turbine_model_points` VALUES (1401, '20835', 0, 0, 0, 0, '主轴后轴承1温度高警告', 'var_38444', 'B', 'notdefined', 'var_38444');
INSERT INTO `turbine_model_points` VALUES (1402, '20835', 0, 0, 0, 0, '主轴后轴承2温度高警告', 'var_38445', 'B', 'notdefined', 'var_38445');
INSERT INTO `turbine_model_points` VALUES (1403, '20835', 0, 0, 0, 0, '主轴前后轴承温差大警告', 'var_38446', 'B', 'notdefined', 'var_38446');
INSERT INTO `turbine_model_points` VALUES (1404, '20835', 0, 0, 0, 0, '塔基烟感警告', 'var_38447', 'B', 'notdefined', 'var_38447');
INSERT INTO `turbine_model_points` VALUES (1405, '20835', 0, 0, 0, 0, '塔基辅助变压器温度高警告', 'var_38448', 'B', 'notdefined', 'var_38448');
INSERT INTO `turbine_model_points` VALUES (1406, '20835', 0, 0, 0, 0, '转子刹车2磨损警告', 'var_38449', 'B', 'notdefined', 'var_38449');
INSERT INTO `turbine_model_points` VALUES (1407, '20835', 0, 0, 0, 0, '转子刹车位置反馈错误故障', 'var_38450', 'B', 'notdefined', 'var_38450');
INSERT INTO `turbine_model_points` VALUES (1408, '20835', 0, 0, 0, 0, '转子刹车未释放故障', 'var_38451', 'B', 'notdefined', 'var_38451');
INSERT INTO `turbine_model_points` VALUES (1409, '20835', 0, 0, 0, 0, '主轴润滑油位低警告', 'var_38452', 'B', 'notdefined', 'var_38452');
INSERT INTO `turbine_model_points` VALUES (1410, '20835', 0, 0, 0, 0, '主轴润滑油温高警告', 'var_38453', 'B', 'notdefined', 'var_38453');
INSERT INTO `turbine_model_points` VALUES (1411, '20835', 0, 0, 0, 0, '主轴润滑堵塞警告', 'var_38454', 'B', 'notdefined', 'var_38454');
INSERT INTO `turbine_model_points` VALUES (1412, '20835', 0, 0, 0, 0, '主轴润滑泵供电过载故障', 'var_38455', 'B', 'notdefined', 'var_38455');
INSERT INTO `turbine_model_points` VALUES (1413, '20835', 0, 0, 0, 0, '主轴润滑出口油压高故障', 'var_38456', 'B', 'notdefined', 'var_38456');
INSERT INTO `turbine_model_points` VALUES (1414, '20835', 0, 0, 0, 0, '主轴润滑前端进口油压高故障', 'var_38457', 'B', 'notdefined', 'var_38457');
INSERT INTO `turbine_model_points` VALUES (1415, '20835', 0, 0, 0, 0, '主轴润滑前端进口油压低故障', 'var_38458', 'B', 'notdefined', 'var_38458');
INSERT INTO `turbine_model_points` VALUES (1416, '20835', 0, 0, 0, 0, '主轴润滑后端进口油压高故障', 'var_38459', 'B', 'notdefined', 'var_38459');
INSERT INTO `turbine_model_points` VALUES (1417, '20835', 0, 0, 0, 0, '主轴润滑后端进口油压低故障', 'var_38460', 'B', 'notdefined', 'var_38460');
INSERT INTO `turbine_model_points` VALUES (1418, '20835', 0, 0, 0, 0, 'IPC数据存储内存不足', 'var_38461', 'B', 'notdefined', 'var_38461');
INSERT INTO `turbine_model_points` VALUES (1419, '20835', 0, 0, 0, 0, 'IPC校准完成', 'var_38462', 'B', 'notdefined', 'var_38462');
INSERT INTO `turbine_model_points` VALUES (1420, '20835', 0, 0, 0, 0, 'IPC校准中断', 'var_38463', 'B', 'notdefined', 'var_38463');
INSERT INTO `turbine_model_points` VALUES (1421, '20835', 0, 0, 0, 0, 'IPC正在校准', 'var_38464', 'B', 'notdefined', 'var_38464');
INSERT INTO `turbine_model_points` VALUES (1422, '20835', 0, 0, 0, 0, 'IPC状态1无心跳警告', 'var_38465', 'B', 'notdefined', 'var_38465');
INSERT INTO `turbine_model_points` VALUES (1423, '20835', 0, 0, 0, 0, 'IPC状态2无心跳警告', 'var_38466', 'B', 'notdefined', 'var_38466');
INSERT INTO `turbine_model_points` VALUES (1424, '20835', 0, 0, 0, 0, 'IPC状态3无心跳警告', 'var_38467', 'B', 'notdefined', 'var_38467');
INSERT INTO `turbine_model_points` VALUES (1425, '20835', 0, 0, 0, 0, 'IPC状态4无心跳警告', 'var_38468', 'B', 'notdefined', 'var_38468');
INSERT INTO `turbine_model_points` VALUES (1426, '20835', 0, 0, 0, 0, 'IPC自动校准数据', 'var_38469', 'B', 'notdefined', 'var_38469');
INSERT INTO `turbine_model_points` VALUES (1427, '20835', 0, 0, 0, 0, 'IPC标定未完成警告', 'var_38470', 'B', 'notdefined', 'var_38470');
INSERT INTO `turbine_model_points` VALUES (1428, '20835', 0, 0, 0, 0, 'IPC挥舞载荷异常警告', 'var_38471', 'B', 'notdefined', 'var_38471');
INSERT INTO `turbine_model_points` VALUES (1429, '20835', 0, 0, 0, 0, 'IPC挥舞载荷异常警告2', 'var_38472', 'B', 'notdefined', 'var_38472');
INSERT INTO `turbine_model_points` VALUES (1430, '20835', 0, 0, 0, 0, 'IPC波长异常警告', 'var_38473', 'B', 'notdefined', 'var_38473');
INSERT INTO `turbine_model_points` VALUES (1431, '20835', 0, 0, 0, 0, 'IPC波长异常警告2', 'var_38474', 'B', 'notdefined', 'var_38474');
INSERT INTO `turbine_model_points` VALUES (1432, '20835', 0, 0, 0, 0, '风轮方位角误差警告', 'var_38475', 'B', 'notdefined', 'var_38475');
INSERT INTO `turbine_model_points` VALUES (1433, '20835', 0, 0, 0, 0, '风轮移动位置故障', 'var_38476', 'B', 'notdefined', 'var_38476');
INSERT INTO `turbine_model_points` VALUES (1434, '20835', 0, 0, 0, 0, 'IPC通讯故障', 'var_38477', 'B', 'notdefined', 'var_38477');
INSERT INTO `turbine_model_points` VALUES (1435, '20835', 0, 0, 0, 0, '塔基动力电缆温度故障警告', 'var_38478', 'B', 'notdefined', 'var_38478');
INSERT INTO `turbine_model_points` VALUES (1436, '20835', 0, 0, 0, 0, '机舱一级消防消防故障', 'var_38479', 'B', 'notdefined', 'var_38479');
INSERT INTO `turbine_model_points` VALUES (1437, '20835', 0, 0, 0, 0, 'A30控制柜消防系统动作', 'var_38480', 'B', 'notdefined', 'var_38480');
INSERT INTO `turbine_model_points` VALUES (1438, '20835', 0, 0, 0, 0, '变流器消防系统动作', 'var_38481', 'B', 'notdefined', 'var_38481');
INSERT INTO `turbine_model_points` VALUES (1439, '20835', 0, 0, 0, 0, '箱变消防系统动作', 'var_38482', 'B', 'notdefined', 'var_38482');
INSERT INTO `turbine_model_points` VALUES (1440, '20835', 0, 0, 0, 0, '塔基消防系统动作', 'var_38483', 'B', 'notdefined', 'var_38483');
INSERT INTO `turbine_model_points` VALUES (1441, '20835', 0, 0, 0, 0, '机舱消防系统动作', 'var_38484', 'B', 'notdefined', 'var_38484');
INSERT INTO `turbine_model_points` VALUES (1442, '20835', 0, 0, 0, 0, '齿轮箱油泵电机3过载', 'var_38485', 'B', 'notdefined', 'var_38485');
INSERT INTO `turbine_model_points` VALUES (1443, '20835', 0, 0, 0, 0, '环网柜控制电源消失警告', 'var_38486', 'B', 'notdefined', 'var_38486');
INSERT INTO `turbine_model_points` VALUES (1444, '20835', 0, 0, 0, 0, '环网柜继电保护装置故障反馈警告', 'var_38487', 'B', 'notdefined', 'var_38487');
INSERT INTO `turbine_model_points` VALUES (1445, '20835', 0, 0, 0, 0, '弧光保护装置呼唤警告', 'var_38488', 'B', 'notdefined', 'var_38488');
INSERT INTO `turbine_model_points` VALUES (1446, '20835', 0, 0, 0, 0, '弧光保护装置激活故障', 'var_38489', 'B', 'notdefined', 'var_38489');
INSERT INTO `turbine_model_points` VALUES (1447, '20835', 0, 0, 0, 0, 'G—Sensor1加速度瞬时超限', 'var_38490', 'B', 'notdefined', 'var_38490');
INSERT INTO `turbine_model_points` VALUES (1448, '20835', 0, 0, 0, 0, '偏航断路器单元电阻过载', 'var_38491', 'B', 'notdefined', 'var_38491');
INSERT INTO `turbine_model_points` VALUES (1449, '20835', 0, 0, 0, 0, '转子刹车投入压力高警告', 'var_38492', 'B', 'notdefined', 'var_38492');
INSERT INTO `turbine_model_points` VALUES (1450, '20835', 0, 0, 0, 0, '塔基辅助变压器温度高故障', 'var_38493', 'B', 'notdefined', 'var_38493');
INSERT INTO `turbine_model_points` VALUES (1451, '20835', 0, 0, 0, 0, '变压器顶层油温传感器故障', 'var_38494', 'B', 'notdefined', 'var_38494');
INSERT INTO `turbine_model_points` VALUES (1452, '20835', 0, 0, 0, 0, '变压器缺油故障', 'var_38495', 'B', 'notdefined', 'var_38495');
INSERT INTO `turbine_model_points` VALUES (1453, '20835', 0, 0, 0, 0, '环网柜继电保护装置故障', 'var_38496', 'B', 'notdefined', 'var_38496');
INSERT INTO `turbine_model_points` VALUES (1454, '20835', 0, 0, 0, 0, '环网柜SF6气压警告', 'var_38497', 'B', 'notdefined', 'var_38497');
INSERT INTO `turbine_model_points` VALUES (1455, '20835', 0, 0, 0, 0, '环网柜C1高压负荷开关异常警告', 'var_38498', 'B', 'notdefined', 'var_38498');
INSERT INTO `turbine_model_points` VALUES (1456, '20835', 0, 0, 0, 0, '环网柜C2高压负荷开关异常警告', 'var_38499', 'B', 'notdefined', 'var_38499');
INSERT INTO `turbine_model_points` VALUES (1457, '20835', 0, 0, 0, 0, '环网柜V断路器异常警告', 'var_38500', 'B', 'notdefined', 'var_38500');
INSERT INTO `turbine_model_points` VALUES (1458, '20835', 0, 0, 0, 0, 'SCADA远程断开C3柜停机', 'var_38501', 'B', 'notdefined', 'var_38501');
INSERT INTO `turbine_model_points` VALUES (1459, '20835', 0, 0, 0, 0, 'SCADA远程断开C3柜警告', 'var_38502', 'B', 'notdefined', 'var_38502');
INSERT INTO `turbine_model_points` VALUES (1460, '20835', 0, 0, 0, 0, '环网柜C3高压负荷开关位置警告', 'var_38503', 'B', 'notdefined', 'var_38503');
INSERT INTO `turbine_model_points` VALUES (1461, '20835', 0, 0, 0, 0, '变压器重瓦斯跳闸开关断线故障', 'var_38504', 'B', 'notdefined', 'var_38504');
INSERT INTO `turbine_model_points` VALUES (1462, '20835', 0, 0, 0, 0, '变压器超温跳闸开关断线故障', 'var_38505', 'B', 'notdefined', 'var_38505');
INSERT INTO `turbine_model_points` VALUES (1463, '20835', 0, 0, 0, 0, '变压器压力阀跳闸开关断线故障', 'var_38506', 'B', 'notdefined', 'var_38506');
INSERT INTO `turbine_model_points` VALUES (1464, '20835', 0, 0, 0, 0, '环网柜断路器闭锁警告', 'var_38507', 'B', 'notdefined', 'var_38507');
INSERT INTO `turbine_model_points` VALUES (1465, '20835', 0, 0, 0, 0, '环网柜断路器机构警告', 'var_38508', 'B', 'notdefined', 'var_38508');
INSERT INTO `turbine_model_points` VALUES (1466, '20835', 0, 0, 0, 0, '环网柜继电保护装置心跳故障', 'var_38509', 'B', 'notdefined', 'var_38509');
INSERT INTO `turbine_model_points` VALUES (1467, '20835', 0, 0, 0, 0, '风速超出设计范围故障', 'var_38510', 'B', 'notdefined', 'var_38510');
INSERT INTO `turbine_model_points` VALUES (1468, '20835', 0, 0, 0, 0, '风轮锁位置警告', 'var_38511', 'B', 'notdefined', 'var_38511');
INSERT INTO `turbine_model_points` VALUES (1469, '20835', 0, 0, 0, 0, '后备电源通讯错误警告', 'var_38512', 'B', 'notdefined', 'var_38512');
INSERT INTO `turbine_model_points` VALUES (1470, '20835', 0, 0, 0, 0, '主控系统给定1#叶片参考角度', 'var_18028', 'F', '°', 'var_18028');
INSERT INTO `turbine_model_points` VALUES (1471, '20835', 0, 0, 0, 0, '主控系统给定2#叶片参考角度', 'var_18029', 'F', '°', 'var_18029');
INSERT INTO `turbine_model_points` VALUES (1472, '20835', 0, 0, 0, 0, '有功功率最大设定值', 'var_50', 'F', 'kW', 'var_50');
INSERT INTO `turbine_model_points` VALUES (1473, '20835', 0, 0, 0, 0, '主控系统给定3#叶片参考角度', 'var_18030', 'F', '°', 'var_18030');
INSERT INTO `turbine_model_points` VALUES (1474, '20835', 0, 0, 0, 0, '自耗电A相电流1s均值', 'var_28004', 'F', 'A', 'var_28004');
INSERT INTO `turbine_model_points` VALUES (1475, '20835', 0, 0, 0, 0, '自耗电B相电流1s均值', 'var_28005', 'F', 'A', 'var_28005');
INSERT INTO `turbine_model_points` VALUES (1476, '20835', 0, 0, 0, 0, '自耗电C相电流1s均值', 'var_28006', 'F', 'A', 'var_28006');
INSERT INTO `turbine_model_points` VALUES (1477, '20835', 0, 0, 0, 0, '自耗电有功1s均值', 'var_28007', 'F', 'KW', 'var_28007');
INSERT INTO `turbine_model_points` VALUES (1478, '20835', 0, 0, 0, 0, '自耗电有功10min均值', 'var_28008', 'F', 'KW', 'var_28008');
INSERT INTO `turbine_model_points` VALUES (1479, '20835', 0, 0, 0, 0, '自耗电无功1s均值', 'var_28009', 'F', 'kVAr', 'var_28009');
INSERT INTO `turbine_model_points` VALUES (1480, '20835', 0, 0, 0, 0, '主控调试软件操作记录16', 'var_23523', 'I', 'notdefined', 'var_23523');
INSERT INTO `turbine_model_points` VALUES (1481, '20835', 0, 0, 0, 0, '主控调试软件操作记录17', 'var_23524', 'I', 'notdefined', 'var_23524');
INSERT INTO `turbine_model_points` VALUES (1482, '20835', 0, 0, 0, 0, '主控调试软件操作记录18', 'var_23525', 'I', 'notdefined', 'var_23525');
INSERT INTO `turbine_model_points` VALUES (1483, '20835', 0, 0, 0, 0, '主控调试软件操作记录19', 'var_23526', 'I', 'notdefined', 'var_23526');
INSERT INTO `turbine_model_points` VALUES (1484, '20835', 0, 0, 0, 0, '主控调试软件操作记录20', 'var_23527', 'I', 'notdefined', 'var_23527');
INSERT INTO `turbine_model_points` VALUES (1485, '20835', 0, 0, 0, 0, '主控调试软件操作记录21', 'var_23528', 'I', 'notdefined', 'var_23528');
INSERT INTO `turbine_model_points` VALUES (1486, '20835', 0, 0, 0, 0, '主控调试软件操作记录22', 'var_23529', 'I', 'notdefined', 'var_23529');
INSERT INTO `turbine_model_points` VALUES (1487, '20835', 0, 0, 0, 0, '主控调试软件操作记录23', 'var_23530', 'I', 'notdefined', 'var_23530');
INSERT INTO `turbine_model_points` VALUES (1488, '20835', 0, 0, 0, 0, '主控调试软件操作记录24', 'var_23531', 'I', 'notdefined', 'var_23531');
INSERT INTO `turbine_model_points` VALUES (1489, '20835', 0, 0, 0, 0, '主控调试软件操作记录25', 'var_23532', 'I', 'notdefined', 'var_23532');
INSERT INTO `turbine_model_points` VALUES (1490, '20835', 0, 0, 0, 0, '主控调试软件操作记录26', 'var_23533', 'I', 'notdefined', 'var_23533');
INSERT INTO `turbine_model_points` VALUES (1491, '20835', 0, 0, 0, 0, '主控调试软件操作记录27', 'var_23534', 'I', 'notdefined', 'var_23534');
INSERT INTO `turbine_model_points` VALUES (1492, '20835', 0, 0, 0, 0, '主控调试软件操作记录28', 'var_23535', 'I', 'notdefined', 'var_23535');
INSERT INTO `turbine_model_points` VALUES (1493, '20835', 0, 0, 0, 0, '主控调试软件操作记录29', 'var_23536', 'I', 'notdefined', 'var_23536');
INSERT INTO `turbine_model_points` VALUES (1494, '20835', 0, 0, 0, 0, '主控调试软件操作记录30', 'var_23537', 'I', 'notdefined', 'var_23537');
INSERT INTO `turbine_model_points` VALUES (1495, '20835', 0, 0, 0, 0, '主控调试软件操作记录31', 'var_23538', 'I', 'notdefined', 'var_23538');
INSERT INTO `turbine_model_points` VALUES (1496, '20835', 0, 0, 0, 0, '主控调试软件操作记录32', 'var_23539', 'I', 'notdefined', 'var_23539');
INSERT INTO `turbine_model_points` VALUES (1497, '20835', 0, 0, 0, 0, '主控调试软件操作记录33', 'var_23540', 'I', 'notdefined', 'var_23540');
INSERT INTO `turbine_model_points` VALUES (1498, '20835', 0, 0, 0, 0, '主控调试软件操作记录1', 'var_23448', 'I', 'notdefined', 'var_23448');
INSERT INTO `turbine_model_points` VALUES (1499, '20835', 0, 0, 0, 0, '主控调试软件操作记录2', 'var_23449', 'I', 'notdefined', 'var_23449');
INSERT INTO `turbine_model_points` VALUES (1500, '20835', 0, 0, 0, 0, '主控调试软件操作记录3', 'var_23450', 'I', 'notdefined', 'var_23450');
INSERT INTO `turbine_model_points` VALUES (1501, '20835', 0, 0, 0, 0, '主控调试软件操作记录4', 'var_23451', 'I', 'notdefined', 'var_23451');
INSERT INTO `turbine_model_points` VALUES (1502, '20835', 0, 0, 0, 0, '主控调试软件操作记录5', 'var_23452', 'I', 'notdefined', 'var_23452');
INSERT INTO `turbine_model_points` VALUES (1503, '20835', 0, 0, 0, 0, '主控调试软件操作记录6', 'var_23453', 'I', 'notdefined', 'var_23453');
INSERT INTO `turbine_model_points` VALUES (1504, '20835', 0, 0, 0, 0, '主控调试软件操作记录7', 'var_23454', 'I', 'notdefined', 'var_23454');
INSERT INTO `turbine_model_points` VALUES (1505, '20835', 0, 0, 0, 0, '主控调试软件操作记录8', 'var_23455', 'I', 'notdefined', 'var_23455');
INSERT INTO `turbine_model_points` VALUES (1506, '20835', 0, 0, 0, 0, '主控调试软件操作记录9', 'var_23456', 'I', 'notdefined', 'var_23456');
INSERT INTO `turbine_model_points` VALUES (1507, '20835', 0, 0, 0, 0, '主控调试软件操作记录10', 'var_23457', 'I', 'notdefined', 'var_23457');
INSERT INTO `turbine_model_points` VALUES (1508, '20835', 0, 0, 0, 0, '主控调试软件操作记录11', 'var_23458', 'I', 'notdefined', 'var_23458');
INSERT INTO `turbine_model_points` VALUES (1509, '20835', 0, 0, 0, 0, '主控调试软件操作记录12', 'var_23459', 'I', 'notdefined', 'var_23459');
INSERT INTO `turbine_model_points` VALUES (1510, '20835', 0, 0, 0, 0, '主控调试软件操作记录13', 'var_23460', 'I', 'notdefined', 'var_23460');
INSERT INTO `turbine_model_points` VALUES (1511, '20835', 0, 0, 0, 0, '主控调试软件操作记录14', 'var_23461', 'I', 'notdefined', 'var_23461');
INSERT INTO `turbine_model_points` VALUES (1512, '20835', 0, 0, 0, 0, '主控调试软件操作记录15', 'var_23462', 'I', 'notdefined', 'var_23462');
INSERT INTO `turbine_model_points` VALUES (1513, '20835', 0, 0, 0, 0, '主控到变桨1控制字', 'var_23549', 'I', 'notdefined', 'var_23549');
INSERT INTO `turbine_model_points` VALUES (1514, '20835', 0, 0, 0, 0, '主控到变桨2控制字', 'var_23550', 'I', 'notdefined', 'var_23550');
INSERT INTO `turbine_model_points` VALUES (1515, '20835', 0, 0, 0, 0, '主控到变桨3控制字', 'var_23551', 'I', 'notdefined', 'var_23551');
INSERT INTO `turbine_model_points` VALUES (1516, '20835', 0, 0, 0, 0, '变桨1到主控状态字1 ', 'var_23552', 'I', 'notdefined', 'var_23552');
INSERT INTO `turbine_model_points` VALUES (1517, '20835', 0, 0, 0, 0, '变桨2到主控状态字1 ', 'var_23553', 'I', 'notdefined', 'var_23553');
INSERT INTO `turbine_model_points` VALUES (1518, '20835', 0, 0, 0, 0, '变桨3到主控状态字1 ', 'var_23554', 'I', 'notdefined', 'var_23554');
INSERT INTO `turbine_model_points` VALUES (1519, '20835', 0, 0, 0, 0, '变桨1到主控状态字2 ', 'var_23555', 'I', 'notdefined', 'var_23555');
INSERT INTO `turbine_model_points` VALUES (1520, '20835', 0, 0, 0, 0, '变桨2到主控状态字2 ', 'var_23556', 'I', 'notdefined', 'var_23556');
INSERT INTO `turbine_model_points` VALUES (1521, '20835', 0, 0, 0, 0, '变桨3到主控状态字2 ', 'var_23557', 'I', 'notdefined', 'var_23557');
INSERT INTO `turbine_model_points` VALUES (1522, '20835', 0, 0, 0, 0, '变桨1到主控状态字3 ', 'var_23558', 'I', 'notdefined', 'var_23558');
INSERT INTO `turbine_model_points` VALUES (1523, '20835', 0, 0, 0, 0, '变桨2到主控状态字3 ', 'var_23559', 'I', 'notdefined', 'var_23559');
INSERT INTO `turbine_model_points` VALUES (1524, '20835', 0, 0, 0, 0, '变桨3到主控状态字3 ', 'var_23560', 'I', 'notdefined', 'var_23560');
INSERT INTO `turbine_model_points` VALUES (1525, '20835', 0, 0, 0, 0, '变桨1到主控状态字4', 'var_23561', 'I', 'notdefined', 'var_23561');
INSERT INTO `turbine_model_points` VALUES (1526, '20835', 0, 0, 0, 0, '变桨2到主控状态字4 ', 'var_23562', 'I', 'notdefined', 'var_23562');
INSERT INTO `turbine_model_points` VALUES (1527, '20835', 0, 0, 0, 0, '变桨3到主控状态字4 ', 'var_23563', 'I', 'notdefined', 'var_23563');
INSERT INTO `turbine_model_points` VALUES (1528, '20835', 0, 0, 0, 0, '变桨2#轮毂温度', 'var_23564', 'I', 'notdefined', 'var_23564');
INSERT INTO `turbine_model_points` VALUES (1529, '20835', 0, 0, 0, 0, '变桨3#轮毂温度', 'var_23565', 'I', 'notdefined', 'var_23565');

-- ----------------------------
-- Table structure for turbine_operation_mode
-- ----------------------------
DROP TABLE IF EXISTS `turbine_operation_mode`;
CREATE TABLE `turbine_operation_mode`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` int NOT NULL,
  `descrption` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_operation_mode
-- ----------------------------
INSERT INTO `turbine_operation_mode` VALUES (1, 1, '初始化');
INSERT INTO `turbine_operation_mode` VALUES (2, 2, '停机');
INSERT INTO `turbine_operation_mode` VALUES (3, 4, '待机');
INSERT INTO `turbine_operation_mode` VALUES (4, 8, '气动');
INSERT INTO `turbine_operation_mode` VALUES (5, 16, '加速');
INSERT INTO `turbine_operation_mode` VALUES (6, 32, '发电');
INSERT INTO `turbine_operation_mode` VALUES (7, 33, '限功率发电');
INSERT INTO `turbine_operation_mode` VALUES (8, 34, '降容发电');
INSERT INTO `turbine_operation_mode` VALUES (9, 35, '远方限功率');
INSERT INTO `turbine_operation_mode` VALUES (10, 36, '就地限功率');
INSERT INTO `turbine_operation_mode` VALUES (11, 64, '维护');
INSERT INTO `turbine_operation_mode` VALUES (12, 97, '自身故障');
INSERT INTO `turbine_operation_mode` VALUES (13, 96, '非自身故障');
INSERT INTO `turbine_operation_mode` VALUES (14, 100, '通讯中断');
INSERT INTO `turbine_operation_mode` VALUES (15, 101, '警告');

-- ----------------------------
-- Table structure for turbine_variable_bound
-- ----------------------------
DROP TABLE IF EXISTS `turbine_variable_bound`;
CREATE TABLE `turbine_variable_bound`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '20835' COMMENT 'model_point对应字段',
  `var_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'model_point对应字段',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '需要显示的中文名称',
  `lower_bound` float NOT NULL DEFAULT -999.999 COMMENT '报警下限，单位与model_point一致',
  `upper_bound` float NOT NULL DEFAULT 100 COMMENT '报警上限，单位与model_point一致',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `var_name`(`var_name` ASC) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE,
  CONSTRAINT `turbine_variable_bound_ibfk_1` FOREIGN KEY (`set_id`) REFERENCES `windfarm_infomation` (`set_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 38 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_variable_bound
-- ----------------------------
INSERT INTO `turbine_variable_bound` VALUES (1, '20835', 'var_171', '齿轮箱HS1轴承温度', -999.999, 90);
INSERT INTO `turbine_variable_bound` VALUES (2, '20835', 'var_172', '齿轮箱HS2轴承温度', -999.999, 90);
INSERT INTO `turbine_variable_bound` VALUES (3, '20835', 'var_175', '齿轮箱油池温度', -100, 75);
INSERT INTO `turbine_variable_bound` VALUES (4, '20835', 'var_182', '齿轮箱进口压力', 0.3, 11);
INSERT INTO `turbine_variable_bound` VALUES (5, '20835', 'var_2713', '齿轮箱过滤器1压差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (6, '20835', 'var_2714', '齿轮箱过滤器2压差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (7, '20835', 'var_2715', '齿轮箱过滤器3压差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (8, '20835', 'var_104', '1#叶片冗余变桨角度', -999.999, 91);
INSERT INTO `turbine_variable_bound` VALUES (9, '20835', 'var_105', '2#叶片冗余变桨角度', -999.999, 91);
INSERT INTO `turbine_variable_bound` VALUES (10, '20835', 'abs(var_171-var_172)', '前后主轴承温绝对差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (11, '20835', 'abs(var_104-var_105)', '1#-2#叶片角度绝对差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (12, '20835', 'var_206', '发电机绕组u1温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (13, '20835', 'var_207', '发电机绕组u2温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (14, '20835', 'var_208', '发电机绕组v1温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (15, '20835', 'var_209', '发电机绕组v2温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (16, '20835', 'var_210', '发电机绕组w1温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (17, '20835', 'var_211', '发电机绕组w2温度', -999.999, 145);
INSERT INTO `turbine_variable_bound` VALUES (18, '20835', 'var_106', '3#叶片冗余变桨角度', -999.999, 91);
INSERT INTO `turbine_variable_bound` VALUES (19, '20835', 'abs(var_104-var_106)', '1#-3#叶片角度绝对差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (20, '20835', 'abs(var_105-var_106)', '1#-2#叶片角度绝对差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (21, '20835', 'var_15004', '变流器机侧A相电流', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (22, '20835', 'var_15005', '变流器机侧B相电流', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (23, '20835', 'var_15006', '变流器机侧C相电流', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (24, '20835', 'var_12016', '变流器入水口温度反馈', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (25, '20835', 'var_18000', '叶根载荷监测叶片1摆振弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (26, '20835', 'var_18001', '叶根载荷监测叶片2摆振弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (27, '20835', 'var_18002', '叶根载荷监测叶片3摆振弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (28, '20835', 'var_18003', '叶根载荷监测叶片1挥舞弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (29, '20835', 'var_18004', '叶根载荷监测叶片2挥舞弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (30, '20835', 'var_18005', '叶根载荷监测叶片3挥舞弯矩', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (31, '20835', 'var_246', '电网有功功率', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (32, '20835', 'abs(avg(var_18003)-avg(var_18004))', '1#-2#叶片挥舞弯矩差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (33, '20835', 'abs(avg(var_18003)-avg(var_18005))', '1#-3#叶片挥舞弯矩差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (34, '20835', 'abs(avg(var_18004)-avg(var_18005))', '2#-3#叶片挥舞弯矩差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (35, '20835', 'abs(avg(var_18000)-avg(var_18001))', '1#-2#叶片摆振弯矩差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (36, '20835', 'abs(avg(var_18000)-avg(var_18002))', '1#-3#叶片摆振弯矩差', -999.999, 999.999);
INSERT INTO `turbine_variable_bound` VALUES (37, '20835', 'abs(avg(var_18001)-avg(var_18002))', '2#-3#叶片摆振弯矩差', -999.999, 999.999);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '密码',
  `privilege` int NOT NULL COMMENT '权限，1-具备账号管理功能，2-普通账户',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 15 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', 'pbkdf2:sha256:260000$OBcshGdRulbnvt65$db230312eee30c161807a67f25cb6b2dbcb83b5f36d654b6379c54fc8336bfd9', 1);
INSERT INTO `user` VALUES (13, 'test', 'pbkdf2:sha256:260000$yti3Vh5grrPSQGHD$8277db1b94d3d552e4f9023d8ba1570f690b5227e0f5dee3b565ac648bbf78da', 1);
INSERT INTO `user` VALUES (14, 'test3', 'pbkdf2:sha256:260000$NTCpPeCZ21Wzwcs0$fe93a9d3e43d7fde12fa609d3855115410f397c89dd8a3413ee82f5a4d4cac85', 0);

-- ----------------------------
-- Table structure for windfarm_configuration
-- ----------------------------
DROP TABLE IF EXISTS `windfarm_configuration`;
CREATE TABLE `windfarm_configuration`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的set_id对应',
  `turbine_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的device对应',
  `map_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '现场使用的设备编号',
  `model_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'windfarm_turbine_model键值',
  `gearbox_ratio` float NOT NULL COMMENT '齿轮箱速比',
  `on_grid_date` datetime NULL DEFAULT NULL COMMENT '并网日期',
  PRIMARY KEY (`id`, `turbine_id`, `map_id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE,
  INDEX `turbine_id`(`turbine_id` ASC) USING BTREE,
  INDEX `set_id_2`(`set_id` ASC, `turbine_id` ASC) USING BTREE,
  INDEX `windfarm_configuration_ibfk_1`(`set_id` ASC, `model_name` ASC) USING BTREE,
  CONSTRAINT `windfarm_configuration_ibfk_1` FOREIGN KEY (`set_id`, `model_name`) REFERENCES `windfarm_turbine_model` (`set_id`, `model_name`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 119 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of windfarm_configuration
-- ----------------------------
INSERT INTO `windfarm_configuration` VALUES (61, '20835', 's10001', 'F001', '20835', 107, NULL);
INSERT INTO `windfarm_configuration` VALUES (62, '20835', 's10003', 'F002', '20835', 107, NULL);

-- ----------------------------
-- Table structure for windfarm_infomation
-- ----------------------------
DROP TABLE IF EXISTS `windfarm_infomation`;
CREATE TABLE `windfarm_infomation`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `farm_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '风场名',
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '20835' COMMENT '对应tdengine里的set_id',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of windfarm_infomation
-- ----------------------------
INSERT INTO `windfarm_infomation` VALUES (1, 'bozhong', '20835');

-- ----------------------------
-- Table structure for windfarm_power_curve
-- ----------------------------
DROP TABLE IF EXISTS `windfarm_power_curve`;
CREATE TABLE `windfarm_power_curve`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `mean_speed` float NOT NULL,
  `mean_power` float NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `model_name`(`model_name` ASC) USING BTREE,
  CONSTRAINT `windfarm_power_curve_ibfk_1` FOREIGN KEY (`model_name`) REFERENCES `windfarm_turbine_model` (`model_name`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 443 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of windfarm_power_curve
-- ----------------------------
INSERT INTO `windfarm_power_curve` VALUES (222, '20835', 3, 175);
INSERT INTO `windfarm_power_curve` VALUES (223, '20835', 3.1, 223.2);
INSERT INTO `windfarm_power_curve` VALUES (224, '20835', 3.2, 271.4);
INSERT INTO `windfarm_power_curve` VALUES (225, '20835', 3.3, 319.6);
INSERT INTO `windfarm_power_curve` VALUES (226, '20835', 3.4, 367.8);
INSERT INTO `windfarm_power_curve` VALUES (227, '20835', 3.5, 416);
INSERT INTO `windfarm_power_curve` VALUES (228, '20835', 3.6, 464.2);
INSERT INTO `windfarm_power_curve` VALUES (229, '20835', 3.7, 512.4);
INSERT INTO `windfarm_power_curve` VALUES (230, '20835', 3.8, 560.6);
INSERT INTO `windfarm_power_curve` VALUES (231, '20835', 3.9, 608.8);
INSERT INTO `windfarm_power_curve` VALUES (232, '20835', 4, 657);
INSERT INTO `windfarm_power_curve` VALUES (233, '20835', 4.1, 721.6);
INSERT INTO `windfarm_power_curve` VALUES (234, '20835', 4.2, 786.2);
INSERT INTO `windfarm_power_curve` VALUES (235, '20835', 4.3, 850.8);
INSERT INTO `windfarm_power_curve` VALUES (236, '20835', 4.4, 915.4);
INSERT INTO `windfarm_power_curve` VALUES (237, '20835', 4.5, 980);
INSERT INTO `windfarm_power_curve` VALUES (238, '20835', 4.6, 1058.4);
INSERT INTO `windfarm_power_curve` VALUES (239, '20835', 4.7, 1136.8);
INSERT INTO `windfarm_power_curve` VALUES (240, '20835', 4.8, 1215.2);
INSERT INTO `windfarm_power_curve` VALUES (241, '20835', 4.9, 1293.6);
INSERT INTO `windfarm_power_curve` VALUES (242, '20835', 5, 1372);
INSERT INTO `windfarm_power_curve` VALUES (243, '20835', 5.1, 1465.4);
INSERT INTO `windfarm_power_curve` VALUES (244, '20835', 5.2, 1558.8);
INSERT INTO `windfarm_power_curve` VALUES (245, '20835', 5.3, 1652.2);
INSERT INTO `windfarm_power_curve` VALUES (246, '20835', 5.4, 1745.6);
INSERT INTO `windfarm_power_curve` VALUES (247, '20835', 5.5, 1839);
INSERT INTO `windfarm_power_curve` VALUES (248, '20835', 5.6, 1951);
INSERT INTO `windfarm_power_curve` VALUES (249, '20835', 5.7, 2063);
INSERT INTO `windfarm_power_curve` VALUES (250, '20835', 5.8, 2175);
INSERT INTO `windfarm_power_curve` VALUES (251, '20835', 5.9, 2287);
INSERT INTO `windfarm_power_curve` VALUES (252, '20835', 6, 2399);
INSERT INTO `windfarm_power_curve` VALUES (253, '20835', 6.1, 2531.6);
INSERT INTO `windfarm_power_curve` VALUES (254, '20835', 6.2, 2664.2);
INSERT INTO `windfarm_power_curve` VALUES (255, '20835', 6.3, 2796.8);
INSERT INTO `windfarm_power_curve` VALUES (256, '20835', 6.4, 2929.4);
INSERT INTO `windfarm_power_curve` VALUES (257, '20835', 6.5, 3062);
INSERT INTO `windfarm_power_curve` VALUES (258, '20835', 6.6, 3216.2);
INSERT INTO `windfarm_power_curve` VALUES (259, '20835', 6.7, 3370.4);
INSERT INTO `windfarm_power_curve` VALUES (260, '20835', 6.8, 3524.6);
INSERT INTO `windfarm_power_curve` VALUES (261, '20835', 6.9, 3678.8);
INSERT INTO `windfarm_power_curve` VALUES (262, '20835', 7, 3833);
INSERT INTO `windfarm_power_curve` VALUES (263, '20835', 7.1, 4007.4);
INSERT INTO `windfarm_power_curve` VALUES (264, '20835', 7.2, 4181.8);
INSERT INTO `windfarm_power_curve` VALUES (265, '20835', 7.3, 4356.2);
INSERT INTO `windfarm_power_curve` VALUES (266, '20835', 7.4, 4530.6);
INSERT INTO `windfarm_power_curve` VALUES (267, '20835', 7.5, 4705);
INSERT INTO `windfarm_power_curve` VALUES (268, '20835', 7.6, 4893.8);
INSERT INTO `windfarm_power_curve` VALUES (269, '20835', 7.7, 5082.6);
INSERT INTO `windfarm_power_curve` VALUES (270, '20835', 7.8, 5271.4);
INSERT INTO `windfarm_power_curve` VALUES (271, '20835', 7.9, 5460.2);
INSERT INTO `windfarm_power_curve` VALUES (272, '20835', 8, 5649);
INSERT INTO `windfarm_power_curve` VALUES (273, '20835', 8.1, 5830.8);
INSERT INTO `windfarm_power_curve` VALUES (274, '20835', 8.2, 6012.6);
INSERT INTO `windfarm_power_curve` VALUES (275, '20835', 8.3, 6194.4);
INSERT INTO `windfarm_power_curve` VALUES (276, '20835', 8.4, 6376.2);
INSERT INTO `windfarm_power_curve` VALUES (277, '20835', 8.5, 6558);
INSERT INTO `windfarm_power_curve` VALUES (278, '20835', 8.6, 6712.6);
INSERT INTO `windfarm_power_curve` VALUES (279, '20835', 8.7, 6867.2);
INSERT INTO `windfarm_power_curve` VALUES (280, '20835', 8.8, 7021.8);
INSERT INTO `windfarm_power_curve` VALUES (281, '20835', 8.9, 7176.4);
INSERT INTO `windfarm_power_curve` VALUES (282, '20835', 9, 7331);
INSERT INTO `windfarm_power_curve` VALUES (283, '20835', 9.1, 7436.8);
INSERT INTO `windfarm_power_curve` VALUES (284, '20835', 9.2, 7542.6);
INSERT INTO `windfarm_power_curve` VALUES (285, '20835', 9.3, 7648.4);
INSERT INTO `windfarm_power_curve` VALUES (286, '20835', 9.4, 7754.2);
INSERT INTO `windfarm_power_curve` VALUES (287, '20835', 9.5, 7860);
INSERT INTO `windfarm_power_curve` VALUES (288, '20835', 9.6, 7917.8);
INSERT INTO `windfarm_power_curve` VALUES (289, '20835', 9.7, 7975.6);
INSERT INTO `windfarm_power_curve` VALUES (290, '20835', 9.8, 8033.4);
INSERT INTO `windfarm_power_curve` VALUES (291, '20835', 9.9, 8091.2);
INSERT INTO `windfarm_power_curve` VALUES (292, '20835', 10, 8149);
INSERT INTO `windfarm_power_curve` VALUES (293, '20835', 10.1, 8174.8);
INSERT INTO `windfarm_power_curve` VALUES (294, '20835', 10.2, 8200.6);
INSERT INTO `windfarm_power_curve` VALUES (295, '20835', 10.3, 8226.4);
INSERT INTO `windfarm_power_curve` VALUES (296, '20835', 10.4, 8252.2);
INSERT INTO `windfarm_power_curve` VALUES (297, '20835', 10.5, 8278);
INSERT INTO `windfarm_power_curve` VALUES (298, '20835', 10.6, 8287.8);
INSERT INTO `windfarm_power_curve` VALUES (299, '20835', 10.7, 8297.6);
INSERT INTO `windfarm_power_curve` VALUES (300, '20835', 10.8, 8307.4);
INSERT INTO `windfarm_power_curve` VALUES (301, '20835', 10.9, 8317.2);
INSERT INTO `windfarm_power_curve` VALUES (302, '20835', 11, 8327);
INSERT INTO `windfarm_power_curve` VALUES (303, '20835', 11.1, 8330.4);
INSERT INTO `windfarm_power_curve` VALUES (304, '20835', 11.2, 8333.8);
INSERT INTO `windfarm_power_curve` VALUES (305, '20835', 11.3, 8337.2);
INSERT INTO `windfarm_power_curve` VALUES (306, '20835', 11.4, 8340.6);
INSERT INTO `windfarm_power_curve` VALUES (307, '20835', 11.5, 8344);
INSERT INTO `windfarm_power_curve` VALUES (308, '20835', 11.6, 8345.2);
INSERT INTO `windfarm_power_curve` VALUES (309, '20835', 11.7, 8346.4);
INSERT INTO `windfarm_power_curve` VALUES (310, '20835', 11.8, 8347.6);
INSERT INTO `windfarm_power_curve` VALUES (311, '20835', 11.9, 8348.8);
INSERT INTO `windfarm_power_curve` VALUES (312, '20835', 12, 8350);
INSERT INTO `windfarm_power_curve` VALUES (313, '20835', 12.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (314, '20835', 12.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (315, '20835', 12.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (316, '20835', 12.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (317, '20835', 12.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (318, '20835', 12.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (319, '20835', 12.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (320, '20835', 12.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (321, '20835', 12.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (322, '20835', 13, 8350);
INSERT INTO `windfarm_power_curve` VALUES (323, '20835', 13.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (324, '20835', 13.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (325, '20835', 13.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (326, '20835', 13.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (327, '20835', 13.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (328, '20835', 13.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (329, '20835', 13.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (330, '20835', 13.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (331, '20835', 13.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (332, '20835', 14, 8350);
INSERT INTO `windfarm_power_curve` VALUES (333, '20835', 14.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (334, '20835', 14.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (335, '20835', 14.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (336, '20835', 14.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (337, '20835', 14.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (338, '20835', 14.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (339, '20835', 14.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (340, '20835', 14.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (341, '20835', 14.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (342, '20835', 15, 8350);
INSERT INTO `windfarm_power_curve` VALUES (343, '20835', 15.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (344, '20835', 15.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (345, '20835', 15.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (346, '20835', 15.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (347, '20835', 15.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (348, '20835', 15.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (349, '20835', 15.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (350, '20835', 15.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (351, '20835', 15.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (352, '20835', 16, 8350);
INSERT INTO `windfarm_power_curve` VALUES (353, '20835', 16.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (354, '20835', 16.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (355, '20835', 16.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (356, '20835', 16.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (357, '20835', 16.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (358, '20835', 16.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (359, '20835', 16.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (360, '20835', 16.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (361, '20835', 16.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (362, '20835', 17, 8350);
INSERT INTO `windfarm_power_curve` VALUES (363, '20835', 17.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (364, '20835', 17.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (365, '20835', 17.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (366, '20835', 17.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (367, '20835', 17.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (368, '20835', 17.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (369, '20835', 17.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (370, '20835', 17.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (371, '20835', 17.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (372, '20835', 18, 8350);
INSERT INTO `windfarm_power_curve` VALUES (373, '20835', 18.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (374, '20835', 18.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (375, '20835', 18.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (376, '20835', 18.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (377, '20835', 18.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (378, '20835', 18.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (379, '20835', 18.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (380, '20835', 18.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (381, '20835', 18.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (382, '20835', 19, 8350);
INSERT INTO `windfarm_power_curve` VALUES (383, '20835', 19.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (384, '20835', 19.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (385, '20835', 19.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (386, '20835', 19.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (387, '20835', 19.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (388, '20835', 19.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (389, '20835', 19.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (390, '20835', 19.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (391, '20835', 19.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (392, '20835', 20, 8350);
INSERT INTO `windfarm_power_curve` VALUES (393, '20835', 20.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (394, '20835', 20.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (395, '20835', 20.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (396, '20835', 20.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (397, '20835', 20.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (398, '20835', 20.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (399, '20835', 20.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (400, '20835', 20.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (401, '20835', 20.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (402, '20835', 21, 8350);
INSERT INTO `windfarm_power_curve` VALUES (403, '20835', 21.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (404, '20835', 21.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (405, '20835', 21.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (406, '20835', 21.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (407, '20835', 21.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (408, '20835', 21.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (409, '20835', 21.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (410, '20835', 21.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (411, '20835', 21.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (412, '20835', 22, 8350);
INSERT INTO `windfarm_power_curve` VALUES (413, '20835', 22.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (414, '20835', 22.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (415, '20835', 22.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (416, '20835', 22.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (417, '20835', 22.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (418, '20835', 22.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (419, '20835', 22.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (420, '20835', 22.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (421, '20835', 22.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (422, '20835', 23, 8350);
INSERT INTO `windfarm_power_curve` VALUES (423, '20835', 23.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (424, '20835', 23.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (425, '20835', 23.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (426, '20835', 23.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (427, '20835', 23.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (428, '20835', 23.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (429, '20835', 23.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (430, '20835', 23.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (431, '20835', 23.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (432, '20835', 24, 8350);
INSERT INTO `windfarm_power_curve` VALUES (433, '20835', 24.1, 8350);
INSERT INTO `windfarm_power_curve` VALUES (434, '20835', 24.2, 8350);
INSERT INTO `windfarm_power_curve` VALUES (435, '20835', 24.3, 8350);
INSERT INTO `windfarm_power_curve` VALUES (436, '20835', 24.4, 8350);
INSERT INTO `windfarm_power_curve` VALUES (437, '20835', 24.5, 8350);
INSERT INTO `windfarm_power_curve` VALUES (438, '20835', 24.6, 8350);
INSERT INTO `windfarm_power_curve` VALUES (439, '20835', 24.7, 8350);
INSERT INTO `windfarm_power_curve` VALUES (440, '20835', 24.8, 8350);
INSERT INTO `windfarm_power_curve` VALUES (441, '20835', 24.9, 8350);
INSERT INTO `windfarm_power_curve` VALUES (442, '20835', 25, 8350);

-- ----------------------------
-- Table structure for windfarm_turbine_model
-- ----------------------------
DROP TABLE IF EXISTS `windfarm_turbine_model`;
CREATE TABLE `windfarm_turbine_model`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '20835',
  `model_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '配置名',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `model_name`(`model_name` ASC) USING BTREE,
  INDEX `set_id`(`set_id` ASC, `model_name` ASC) USING BTREE,
  CONSTRAINT `windfarm_turbine_model_ibfk_1` FOREIGN KEY (`set_id`) REFERENCES `windfarm_infomation` (`set_id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of windfarm_turbine_model
-- ----------------------------
INSERT INTO `windfarm_turbine_model` VALUES (1, '20835', '20835');

SET FOREIGN_KEY_CHECKS = 1;
