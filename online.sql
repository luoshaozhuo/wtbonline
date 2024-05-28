/*
 Navicat Premium Data Transfer

 Source Server         : mysql
 Source Server Type    : MySQL
 Source Server Version : 80400 (8.4.0)
 Source Host           : 172.24.164.57:40004
 Source Schema         : online

 Target Server Type    : MySQL
 Target Server Version : 80400 (8.4.0)
 File Encoding         : 65001

 Date: 28/05/2024 16:13:57
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app_configuration
-- ----------------------------
DROP TABLE IF EXISTS `app_configuration`;
CREATE TABLE `app_configuration`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '键值',
  `value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '实际值',
  `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '说明',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '参数设置' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of app_configuration
-- ----------------------------
INSERT INTO `app_configuration` VALUES (1, 'tempdir', '/tmp/wtbonline', '临时目录');
INSERT INTO `app_configuration` VALUES (2, 'report_outpath', '/var/local/wtbonline/report', '报告输出目录');
INSERT INTO `app_configuration` VALUES (3, 'model_path', '/var/local/wtbonline/model', '模型文件输出目录');
INSERT INTO `app_configuration` VALUES (4, 'log_path', '/var/local/wtbonline/log', '日志文件输出目录');
INSERT INTO `app_configuration` VALUES (5, 'cache_lifetime', '7', '数据缓存生存时间，天');
INSERT INTO `app_configuration` VALUES (6, 'session_lifetime', '1', '登录超时时长，天');
INSERT INTO `app_configuration` VALUES (7, 'email_address', 'luoshaozhuo@163.com', '接受报告的邮箱地址，多个地址用\';\'隔开');
INSERT INTO `app_configuration` VALUES (8, 'send_email', '1', '0-不发送，非0-发送');
INSERT INTO `app_configuration` VALUES (9, 'email_account', 'hzfdtest@126.com_YHWERYTJAMTBCLBE_smtp.126.com_25', '用户名_授权码_host_port');

-- ----------------------------
-- Table structure for app_server
-- ----------------------------
DROP TABLE IF EXISTS `app_server`;
CREATE TABLE `app_server`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '服务器名',
  `host` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '地址',
  `version` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据库引擎版本',
  `remote` int NULL DEFAULT NULL COMMENT '是否远程服务器',
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用retapi还是cli接口',
  `port` int NULL DEFAULT NULL COMMENT '端口',
  `user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '用户名',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '密码',
  `database` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '库名',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'tdengine服务器地址、用户名、密码等' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of app_server
-- ----------------------------
INSERT INTO `app_server` VALUES (1, 'tdengine', '192.168.0.12', '2.2.2.10', 1, 'restapi', 6041, 'root', 'gAAAAABk1OpyQl28ffKF6SosFzNjiyF6fKHO-Yy0D8UEEbK8Z9oKcsfsfabTTjWcIz_A2ZbjK6XmoQVNEsS71ThLriL0NF6m8A==', 'scada');
INSERT INTO `app_server` VALUES (2, 'tdengine', '192.168.0.2', '3.1.0.0', 0, 'native', 6030, 'root', 'gAAAAABk1OpyQl28ffKF6SosFzNjiyF6fKHO-Yy0D8UEEbK8Z9oKcsfsfabTTjWcIz_A2ZbjK6XmoQVNEsS71ThLriL0NF6m8A==', 'windfarm');
INSERT INTO `app_server` VALUES (3, 'postgres', '192.168.0.32', '13.14', 1, 'native', 5432, 'postgres', 'gAAAAABl6wDvdSK3zSU24o8pYtVAjauInz-H7paKA5GDmoR8qc4zuKHHG3KUhOiMCVowB1H1ang7xiBQ7uP5qz99dV7uCejPTA==', 'scada');

-- ----------------------------
-- Table structure for apscheduler_jobs
-- ----------------------------
DROP TABLE IF EXISTS `apscheduler_jobs`;
CREATE TABLE `apscheduler_jobs`  (
  `id` varchar(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `next_run_time` double NULL DEFAULT NULL,
  `job_state` blob NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_apscheduler_jobs_next_run_time`(`next_run_time` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '任务队列，apscheduler自动生成' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of apscheduler_jobs
-- ----------------------------

-- ----------------------------
-- Table structure for model
-- ----------------------------
DROP TABLE IF EXISTS `model`;
CREATE TABLE `model`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的set_id对应',
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '与tdengine里的device对应',
  `type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模型类型，如anomaly',
  `uuid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '模型唯一码',
  `start_time` datetime NOT NULL COMMENT '建模数据起始时间',
  `end_time` datetime NOT NULL COMMENT '建模数据结束时间',
  `create_time` datetime NOT NULL COMMENT '本记录生成时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uuid`(`uuid` ASC) USING BTREE,
  UNIQUE INDEX `compoud`(`set_id` ASC, `device_id` ASC, `create_time` ASC) USING BTREE,
  INDEX `turbine_id`(`device_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '异常识别模型记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model
-- ----------------------------

-- ----------------------------
-- Table structure for model_anomaly
-- ----------------------------
DROP TABLE IF EXISTS `model_anomaly`;
CREATE TABLE `model_anomaly`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sample_id` int NOT NULL COMMENT 'statistics_sample的记录ID',
  `bin` datetime NOT NULL COMMENT '样本开始时间',
  `model_uuid` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC) USING BTREE,
  INDEX `turbine_id`(`device_id` ASC) USING BTREE,
  INDEX `sample_id`(`sample_id` ASC) USING BTREE,
  INDEX `set_id_2`(`set_id` ASC, `device_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 80 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '异常识别结果' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_anomaly
-- ----------------------------

-- ----------------------------
-- Table structure for model_label
-- ----------------------------
DROP TABLE IF EXISTS `model_label`;
CREATE TABLE `model_label`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名',
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `sample_id` int NOT NULL COMMENT 'statistics_sample的id',
  `is_anomaly` int NOT NULL COMMENT '是否异常值',
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `username`(`username` ASC) USING BTREE,
  INDEX `set_id_3`(`set_id` ASC, `device_id` ASC) USING BTREE,
  INDEX `turbine_id_1`(`device_id` ASC) USING BTREE,
  INDEX `sample_id`(`sample_id` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '用户数据标注记录' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of model_label
-- ----------------------------

-- ----------------------------
-- Table structure for statistics_fault
-- ----------------------------
DROP TABLE IF EXISTS `statistics_fault`;
CREATE TABLE `statistics_fault`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fault_id` int NOT NULL COMMENT 'turbine_fault_type的id值',
  `value` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'flag/fault/alarm/msg 的值',
  `fault_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'turbine_fault_type的type值',
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `set_id`(`set_id` ASC, `device_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 44286 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of statistics_fault
-- ----------------------------

-- ----------------------------
-- Table structure for statistics_sample
-- ----------------------------
DROP TABLE IF EXISTS `statistics_sample`;
CREATE TABLE `statistics_sample`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `device_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `bin` datetime NOT NULL,
  `evntemp_mean` float NULL DEFAULT NULL,
  `powact_mean` float NULL DEFAULT NULL,
  `powreact_mean` float NULL DEFAULT NULL,
  `var_101_mean` float NULL DEFAULT NULL,
  `var_102_mean` float NULL DEFAULT NULL,
  `var_103_mean` float NULL DEFAULT NULL,
  `var_107_mean` float NULL DEFAULT NULL,
  `var_12031_mean` float NULL DEFAULT NULL,
  `var_226_mean` float NULL DEFAULT NULL,
  `var_246_mean` float NULL DEFAULT NULL,
  `var_363_mean` float NULL DEFAULT NULL,
  `var_382_mean` float NULL DEFAULT NULL,
  `var_383_mean` float NULL DEFAULT NULL,
  `var_407_mean` float NULL DEFAULT NULL,
  `var_409_mean` float NULL DEFAULT NULL,
  `var_412_mean` float NULL DEFAULT NULL,
  `var_94_mean` float NULL DEFAULT NULL,
  `winspd_mean` float NULL DEFAULT NULL,
  `evntemp_rms` float NULL DEFAULT NULL,
  `powact_rms` float NULL DEFAULT NULL,
  `powreact_rms` float NULL DEFAULT NULL,
  `var_101_rms` float NULL DEFAULT NULL,
  `var_102_rms` float NULL DEFAULT NULL,
  `var_103_rms` float NULL DEFAULT NULL,
  `var_107_rms` float NULL DEFAULT NULL,
  `var_12031_rms` float NULL DEFAULT NULL,
  `var_226_rms` float NULL DEFAULT NULL,
  `var_246_rms` float NULL DEFAULT NULL,
  `var_363_rms` float NULL DEFAULT NULL,
  `var_382_rms` float NULL DEFAULT NULL,
  `var_383_rms` float NULL DEFAULT NULL,
  `var_407_rms` float NULL DEFAULT NULL,
  `var_409_rms` float NULL DEFAULT NULL,
  `var_412_rms` float NULL DEFAULT NULL,
  `var_94_rms` float NULL DEFAULT NULL,
  `winspd_rms` float NULL DEFAULT NULL,
  `evntemp_iqr` float NULL DEFAULT NULL,
  `powact_iqr` float NULL DEFAULT NULL,
  `powreact_iqr` float NULL DEFAULT NULL,
  `var_101_iqr` float NULL DEFAULT NULL,
  `var_102_iqr` float NULL DEFAULT NULL,
  `var_103_iqr` float NULL DEFAULT NULL,
  `var_107_iqr` float NULL DEFAULT NULL,
  `var_12031_iqr` float NULL DEFAULT NULL,
  `var_226_iqr` float NULL DEFAULT NULL,
  `var_246_iqr` float NULL DEFAULT NULL,
  `var_363_iqr` float NULL DEFAULT NULL,
  `var_382_iqr` float NULL DEFAULT NULL,
  `var_383_iqr` float NULL DEFAULT NULL,
  `var_407_iqr` float NULL DEFAULT NULL,
  `var_409_iqr` float NULL DEFAULT NULL,
  `var_412_iqr` float NULL DEFAULT NULL,
  `var_94_iqr` float NULL DEFAULT NULL,
  `winspd_iqr` float NULL DEFAULT NULL,
  `evntemp_std` float NULL DEFAULT NULL,
  `powact_std` float NULL DEFAULT NULL,
  `powreact_std` float NULL DEFAULT NULL,
  `var_101_std` float NULL DEFAULT NULL,
  `var_102_std` float NULL DEFAULT NULL,
  `var_103_std` float NULL DEFAULT NULL,
  `var_107_std` float NULL DEFAULT NULL,
  `var_12031_std` float NULL DEFAULT NULL,
  `var_226_std` float NULL DEFAULT NULL,
  `var_246_std` float NULL DEFAULT NULL,
  `var_363_std` float NULL DEFAULT NULL,
  `var_382_std` float NULL DEFAULT NULL,
  `var_383_std` float NULL DEFAULT NULL,
  `var_407_std` float NULL DEFAULT NULL,
  `var_409_std` float NULL DEFAULT NULL,
  `var_412_std` float NULL DEFAULT NULL,
  `var_94_std` float NULL DEFAULT NULL,
  `winspd_std` float NULL DEFAULT NULL,
  `evntemp_skew` float NULL DEFAULT NULL,
  `powact_skew` float NULL DEFAULT NULL,
  `powreact_skew` float NULL DEFAULT NULL,
  `var_101_skew` float NULL DEFAULT NULL,
  `var_102_skew` float NULL DEFAULT NULL,
  `var_103_skew` float NULL DEFAULT NULL,
  `var_107_skew` float NULL DEFAULT NULL,
  `var_12031_skew` float NULL DEFAULT NULL,
  `var_226_skew` float NULL DEFAULT NULL,
  `var_246_skew` float NULL DEFAULT NULL,
  `var_363_skew` float NULL DEFAULT NULL,
  `var_382_skew` float NULL DEFAULT NULL,
  `var_383_skew` float NULL DEFAULT NULL,
  `var_407_skew` float NULL DEFAULT NULL,
  `var_409_skew` float NULL DEFAULT NULL,
  `var_412_skew` float NULL DEFAULT NULL,
  `var_94_skew` float NULL DEFAULT NULL,
  `winspd_skew` float NULL DEFAULT NULL,
  `evntemp_kurt` float NULL DEFAULT NULL,
  `powact_kurt` float NULL DEFAULT NULL,
  `powreact_kurt` float NULL DEFAULT NULL,
  `var_101_kurt` float NULL DEFAULT NULL,
  `var_102_kurt` float NULL DEFAULT NULL,
  `var_103_kurt` float NULL DEFAULT NULL,
  `var_107_kurt` float NULL DEFAULT NULL,
  `var_12031_kurt` float NULL DEFAULT NULL,
  `var_226_kurt` float NULL DEFAULT NULL,
  `var_246_kurt` float NULL DEFAULT NULL,
  `var_363_kurt` float NULL DEFAULT NULL,
  `var_382_kurt` float NULL DEFAULT NULL,
  `var_383_kurt` float NULL DEFAULT NULL,
  `var_407_kurt` float NULL DEFAULT NULL,
  `var_409_kurt` float NULL DEFAULT NULL,
  `var_412_kurt` float NULL DEFAULT NULL,
  `var_94_kurt` float NULL DEFAULT NULL,
  `winspd_kurt` float NULL DEFAULT NULL,
  `evntemp_wf` float NULL DEFAULT NULL,
  `powact_wf` float NULL DEFAULT NULL,
  `powreact_wf` float NULL DEFAULT NULL,
  `var_101_wf` float NULL DEFAULT NULL,
  `var_102_wf` float NULL DEFAULT NULL,
  `var_103_wf` float NULL DEFAULT NULL,
  `var_107_wf` float NULL DEFAULT NULL,
  `var_12031_wf` float NULL DEFAULT NULL,
  `var_226_wf` float NULL DEFAULT NULL,
  `var_246_wf` float NULL DEFAULT NULL,
  `var_363_wf` float NULL DEFAULT NULL,
  `var_382_wf` float NULL DEFAULT NULL,
  `var_383_wf` float NULL DEFAULT NULL,
  `var_407_wf` float NULL DEFAULT NULL,
  `var_409_wf` float NULL DEFAULT NULL,
  `var_412_wf` float NULL DEFAULT NULL,
  `var_94_wf` float NULL DEFAULT NULL,
  `winspd_wf` float NULL DEFAULT NULL,
  `evntemp_crest` float NULL DEFAULT NULL,
  `powact_crest` float NULL DEFAULT NULL,
  `powreact_crest` float NULL DEFAULT NULL,
  `var_101_crest` float NULL DEFAULT NULL,
  `var_102_crest` float NULL DEFAULT NULL,
  `var_103_crest` float NULL DEFAULT NULL,
  `var_107_crest` float NULL DEFAULT NULL,
  `var_12031_crest` float NULL DEFAULT NULL,
  `var_226_crest` float NULL DEFAULT NULL,
  `var_246_crest` float NULL DEFAULT NULL,
  `var_363_crest` float NULL DEFAULT NULL,
  `var_382_crest` float NULL DEFAULT NULL,
  `var_383_crest` float NULL DEFAULT NULL,
  `var_407_crest` float NULL DEFAULT NULL,
  `var_409_crest` float NULL DEFAULT NULL,
  `var_412_crest` float NULL DEFAULT NULL,
  `var_94_crest` float NULL DEFAULT NULL,
  `winspd_crest` float NULL DEFAULT NULL,
  `evntemp_zc` float NULL DEFAULT NULL,
  `powact_zc` float NULL DEFAULT NULL,
  `powreact_zc` float NULL DEFAULT NULL,
  `var_101_zc` float NULL DEFAULT NULL,
  `var_102_zc` float NULL DEFAULT NULL,
  `var_103_zc` float NULL DEFAULT NULL,
  `var_107_zc` float NULL DEFAULT NULL,
  `var_12031_zc` float NULL DEFAULT NULL,
  `var_226_zc` float NULL DEFAULT NULL,
  `var_246_zc` float NULL DEFAULT NULL,
  `var_363_zc` float NULL DEFAULT NULL,
  `var_382_zc` float NULL DEFAULT NULL,
  `var_383_zc` float NULL DEFAULT NULL,
  `var_407_zc` float NULL DEFAULT NULL,
  `var_409_zc` float NULL DEFAULT NULL,
  `var_412_zc` float NULL DEFAULT NULL,
  `var_94_zc` float NULL DEFAULT NULL,
  `winspd_zc` float NULL DEFAULT NULL,
  `evntemp_cv` float NULL DEFAULT NULL,
  `powact_cv` float NULL DEFAULT NULL,
  `powreact_cv` float NULL DEFAULT NULL,
  `var_101_cv` float NULL DEFAULT NULL,
  `var_102_cv` float NULL DEFAULT NULL,
  `var_103_cv` float NULL DEFAULT NULL,
  `var_107_cv` float NULL DEFAULT NULL,
  `var_12031_cv` float NULL DEFAULT NULL,
  `var_226_cv` float NULL DEFAULT NULL,
  `var_246_cv` float NULL DEFAULT NULL,
  `var_363_cv` float NULL DEFAULT NULL,
  `var_382_cv` float NULL DEFAULT NULL,
  `var_383_cv` float NULL DEFAULT NULL,
  `var_407_cv` float NULL DEFAULT NULL,
  `var_409_cv` float NULL DEFAULT NULL,
  `var_412_cv` float NULL DEFAULT NULL,
  `var_94_cv` float NULL DEFAULT NULL,
  `winspd_cv` float NULL DEFAULT NULL,
  `evntemp_imp` float NULL DEFAULT NULL,
  `powact_imp` float NULL DEFAULT NULL,
  `powreact_imp` float NULL DEFAULT NULL,
  `var_101_imp` float NULL DEFAULT NULL,
  `var_102_imp` float NULL DEFAULT NULL,
  `var_103_imp` float NULL DEFAULT NULL,
  `var_107_imp` float NULL DEFAULT NULL,
  `var_12031_imp` float NULL DEFAULT NULL,
  `var_226_imp` float NULL DEFAULT NULL,
  `var_246_imp` float NULL DEFAULT NULL,
  `var_363_imp` float NULL DEFAULT NULL,
  `var_382_imp` float NULL DEFAULT NULL,
  `var_383_imp` float NULL DEFAULT NULL,
  `var_407_imp` float NULL DEFAULT NULL,
  `var_409_imp` float NULL DEFAULT NULL,
  `var_412_imp` float NULL DEFAULT NULL,
  `var_94_imp` float NULL DEFAULT NULL,
  `winspd_imp` float NULL DEFAULT NULL,
  `ongrid_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ongrid_unique` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ongrid_nunique` int NULL DEFAULT NULL,
  `limitpowbool_mode` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `limitpowbool_unique` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `limitpowbool_nunique` int NULL DEFAULT NULL,
  `workmode_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `workmode_unique` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `workmode_nunique` int NULL DEFAULT NULL,
  `totalfaultbool_mode` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `totalfaultbool_unique` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `totalfaultbool_nunique` int NULL DEFAULT NULL,
  `nobs` float NULL DEFAULT NULL,
  `pv_c` float NULL DEFAULT NULL,
  `pv_t` float NULL DEFAULT NULL,
  `pv_ctt` float NULL DEFAULT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `a`(`set_id` ASC, `device_id` ASC, `bin` ASC, `create_time` ASC) USING BTREE,
  INDEX `ix_statistics_sample_bin`(`bin` ASC) USING BTREE,
  INDEX `ix_statistics_sample_turbine_id`(`device_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 258974 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '10分钟样本统计量' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of statistics_sample
-- ----------------------------

-- ----------------------------
-- Table structure for timed_task
-- ----------------------------
DROP TABLE IF EXISTS `timed_task`;
CREATE TABLE `timed_task`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '状态，如create，added，summit，fail',
  `func` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '任务类型',
  `start_time` datetime NOT NULL COMMENT '任务初始开始时间',
  `function_parameter` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '传递给任务函数的参数',
  `task_parameter` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '传递给scheduler的参数',
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `update_time` datetime NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_timed_task_username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '定期任务列表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of timed_task
-- ----------------------------

-- ----------------------------
-- Table structure for timed_task_log
-- ----------------------------
DROP TABLE IF EXISTS `timed_task_log`;
CREATE TABLE `timed_task_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'timed_task的记录id',
  `status` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '事件',
  `update_time` datetime NOT NULL COMMENT '运行开始时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_timed_task_log_task_id`(`task_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '定期任务执行记录' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of timed_task_log
-- ----------------------------

-- ----------------------------
-- Table structure for turbine_fault_type
-- ----------------------------
DROP TABLE IF EXISTS `turbine_fault_type`;
CREATE TABLE `turbine_fault_type`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `is_offshore` int NOT NULL DEFAULT 1 COMMENT '1=海上风机，0=陆上',
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '故障名',
  `cause` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '故障原因',
  `value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '取值',
  `type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'flag/fault/msg/alarm',
  `var_names` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '相关变量名',
  `index` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '\'code\' 或具体var_name',
  `time_span` int NOT NULL DEFAULT 5 COMMENT '绘图时故障开始时间前后时长，单位分钟',
  `graph` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'ordinary' COMMENT '绘图类',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 189 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '故障类型' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_fault_type
-- ----------------------------
INSERT INTO `turbine_fault_type` VALUES (1, 0, '液压系统故障', '偏航补压故障', '12016', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (2, 0, '液压系统故障', '液压油加热过载故障', '12003', 'fault', 'var_22082', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (3, 0, '液压系统故障', '液压泵运行时间超限故障', '12004', 'fault', 'var_398,var_12028,var_412', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (4, 0, '液压系统故障', '液压电机过载故障', '12005', 'fault', 'var_22081', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (5, 0, '液压系统故障', '液压系统压力过高故障', '12009', 'fault', 'var_12028', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (6, 0, '液压系统故障', '偏航液压刹车压力低故障', '12012', 'fault', 'var_412', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (7, 0, '液压系统故障', '转子刹车未释放故障 ', '12011', 'fault', 'var_12027,var_23400', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (8, 0, '液压系统故障', '转子刹车片磨损故障', '14001', 'fault', 'var_1366', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (9, 0, '液压系统故障', '偏航22#电磁阀故障', '12013', 'fault', 'var_412', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (10, 0, '液压系统故障', '未偏航时偏航压力低故障', '12019', 'fault', 'var_412', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (11, 0, '液压系统故障', '液压站压力传感器故障', '12021', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (12, 0, '液压系统故障', '液压系统压力高故障', '12020', 'fault', 'var_12028', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (13, 0, '主轴系统故障', '主轴承前端温度过高故障', '3002', 'fault', 'var_173,var_174,var_12029var_12030,var_42,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (14, 0, '主轴系统故障', '主轴承前端温度2过高故障', '3004', 'fault', 'var_173,var_174,var_12029var_12030,var_42,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (15, 0, '主轴系统故障', '主轴承近端温度过高故障', '3003', 'fault', 'var_173,var_174,var_12029var_12030,var_42,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (16, 0, '主轴系统故障', '主轴承近端温度2过高故障', '3005', 'fault', 'var_173,var_174,var_12029var_12030,var_42,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (17, 0, '主轴系统故障', '主轴承润滑间隔超时故障', '3011', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (18, 0, '主轴系统故障', '主轴承温度传感器故障', '3015', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (19, 0, '齿轮箱故障', '齿轮箱油加热过载故障', '1003', 'fault', 'var_147,var_175', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (20, 0, '齿轮箱故障', '齿轮箱油泵电机过载故障', '1001', 'fault', 'var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (21, 0, '齿轮箱故障', '齿轮箱冷却风扇过载故障', '1002', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (22, 0, '齿轮箱故障', '齿轮箱离线过滤器电机过载故障', '1004', 'fault', 'var_144,var_175', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (23, 0, '齿轮箱故障', '齿轮箱高速轴承温度高故障', '1009', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (24, 0, '齿轮箱故障', '齿轮箱高速轴轴承温度差过大故障', '1010', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (25, 0, '齿轮箱故障', '偏航液压刹车释放压力高故障', '12015', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (26, 0, '齿轮箱故障', '齿轮箱油位过低故障', '1026', 'fault', 'var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (27, 0, '齿轮箱故障', '齿轮箱入口油压力低故障', '1015', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (28, 0, '齿轮箱故障', '齿轮箱出口油压高故障', '1020', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (29, 0, '齿轮箱故障', '齿轮箱油池测量温度超温故障', '1014', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (30, 0, '齿轮箱故障', '齿轮箱油泵电机加热过载故障', '1021', 'fault', 'var_147,var_175', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (31, 0, '齿轮箱故障', '齿轮箱离线过滤器压力开关故障', '1005', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (32, 0, '齿轮箱故障', '齿轮箱油出口压力过低故障', '1018', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (33, 0, '齿轮箱故障', '齿轮箱油池温度过低故障', '1011', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (34, 0, '齿轮箱故障', '齿轮箱轴承温度过高故障', '1023', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (35, 0, '齿轮箱故障', '齿轮箱进出口压差过高故障', '1025', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (36, 0, '齿轮箱故障', '齿轮油进口压力过高故障', '1031', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (37, 0, '齿轮箱故障', '齿轮箱过滤器压差高故障', '1032', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (38, 0, '齿轮箱故障', '齿轮箱分配器温度高故障', '2079', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (39, 0, '齿轮箱故障', '齿轮箱过滤器前端压力过高故障', '1034', 'fault', 'var_40,var_140,var_141,var_175,var_176,var_182,evnTemp', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (40, 0, '齿轮箱故障', '齿轮箱压力传感器故障', '1035', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (41, 0, '齿轮箱故障', '齿轮箱温度传感器故障', '1036', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (42, 0, '齿轮箱故障', '齿轮箱入口油温过高', '1037', 'fault', 'var_40,var_140,var_141,var_171,var_172var_175,var_176,var_182,evnTemp,var_358', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (43, 0, '齿轮箱故障', '变流器系统故障', '11003', 'fault', 'converterFaultCode,var_272,var_274,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (44, 0, '齿轮箱故障', '变流器主断路器触发故障', '11004', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (45, 0, '齿轮箱故障', '变流器Crowbar触发故障', '11005', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (46, 0, '齿轮箱故障', '变流器电网故障', '11007', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (47, 0, '齿轮箱故障', '变流器直流母线电压故障', '11008', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (48, 0, '齿轮箱故障', '变流器网侧模块电流故障', '11009', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (49, 0, '齿轮箱故障', '变流器网侧模块硬件故障', '11010', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (50, 0, '齿轮箱故障', '变流器LVRT激活', '11012', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (51, 0, '齿轮箱故障', '变流器控制过程故障', '11013', 'fault', 'var_228,var_229,var_231,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (52, 0, '齿轮箱故障', '变流器Heartbeat信号失效故障', '11014', 'fault', 'var_22166', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (53, 0, '齿轮箱故障', '变流器超温故障', '11016', 'fault', 'converterFaultCode,var_272,var_274,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (54, 0, '齿轮箱故障', '变流器机侧模块电流故障', '11017', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (55, 0, '齿轮箱故障', '变流器机侧模块硬件故障', '11018', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (56, 0, '齿轮箱故障', '变流器发电机转速故障', '11019', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (57, 0, '齿轮箱故障', '变流器编码器故障', '11020', 'fault', 'converterFaultCode,var_272,var_274,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (58, 0, '齿轮箱故障', '变流器FRT故障', '11021', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (59, 0, '齿轮箱故障', '变流器同步故障', '11022', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (60, 0, '齿轮箱故障', '变流器功率主回路开关故障', '11023', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (61, 0, '齿轮箱故障', '变流器散热风扇故障', '11024', 'fault', 'var_239,var_240', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (62, 0, '齿轮箱故障', '变流器控制系统故障', '11025', 'fault', 'converterFaultCode', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (63, 0, '齿轮箱故障', '变流器定子电流故障', '11026', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (64, 0, '齿轮箱故障', '变流器其它故障', '11027', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (65, 0, '齿轮箱故障', '变流器通讯正在初始化故障', '11092', 'fault', 'converterFaultCode,var_228,var_229,var_231,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (66, 0, '齿轮箱故障', '变流器通讯故障', '11093', 'fault', 'converterFaultCode,var_228,var_229,var_231,var_1758,var_22166', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (67, 0, '齿轮箱故障', '变流器转矩追踪故障', '11094', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022,var_12011,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (68, 0, '齿轮箱故障', '变流器LVRT功率斜率故障', '11096', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (69, 0, '齿轮箱故障', '变流器400V过载故障', '11099', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (70, 0, '齿轮箱故障', '变流器定子电压错误故障', '11105', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022,var_12011,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (71, 0, '齿轮箱故障', '变流器超速', '11122', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022,var_12011,var_12013', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (72, 0, '齿轮箱故障', '变流器未就绪', '11123', 'fault', 'var_228,var_229,var_231,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (73, 0, '齿轮箱故障', '变流器加热请求停机', '11122', 'fault', 'var_228,var_229,var_231,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (74, 0, '齿轮箱故障', '变流器状态未准备好', '11123', 'fault', 'converterFaultCode,var_228,var_229,var_231,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (75, 0, '齿轮箱故障', '变流器IO错误故障', '11106', 'fault', 'converterFaultCode', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (76, 0, '齿轮箱故障', '变流器Chopper错误故障', '11107', 'fault', 'converterFaultCode,var_272,var_274,var_12017,var_12018,var_12019,var_12020,var_12021,var_12022', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (77, 0, '液压系统警告', '偏航补压警告', '12014', 'alarm', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (78, 0, '液压系统警告', '液压系统压力高警告', '12010', 'alarm', 'var_12028', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (79, 0, '液压系统警告', '液压油位低警告', '12001', 'alarm', 'var_22044', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (80, 0, '液压系统警告', '液压油加热过载警告', '12017', 'alarm', 'var_22082', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (81, 0, '液压系统警告', '液压泵运行时间超限警告', '12018', 'alarm', 'var_398', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (82, 0, '液压系统警告', '液压系统压力低警告', '12007', 'alarm', 'var_12028', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (83, 0, '液压系统警告', '液压系统压力高警告', '12008', 'alarm', 'var_12028', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (84, 0, '刹车系统警告', '转子刹车盘预磨损警告', '14000', 'alarm', 'var_23400', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (85, 0, '刹车系统警告', '转子刹车超时警告', '14003', 'alarm', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (86, 0, '刹车系统警告', '转子刹车未释放警告', '19009', 'alarm', 'var_23400、var_12027', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (87, 0, '刹车系统警告', '转子刹车液压低警告', '14004', 'alarm', 'var_12027', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (88, 0, '刹车系统警告', '转子刹车液压高警告', '14005', 'alarm', 'var_12027', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (89, 0, '机组降容', '变流器1单模运行', '11120', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (90, 0, '机组降容', '变流器2单模运行', '11121', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (91, 0, '机组降容', '基于气象站的ECD保护运行', '24010', 'msg', 'var_38793,var_38794,var_2708', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (92, 0, '机组降容', '湍流超过设计运行', '24011', 'msg', 'var_38793', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (93, 0, '机组降容', '齿轮箱油池温度低运行', '24012', 'msg', 'var_175', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (94, 0, '机组降容', '风向偏差大运行', '24013', 'msg', 'var_1834', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (95, 0, '机组降容', '风速波动大运行', '24014', 'msg', 'var_101,var_102,var_103,var_226,var_18000,var_18001,var_18002,var_18003,var_18004,var_18005', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (96, 0, '机组降容', '变流器减载运行', '24015', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (97, 0, '机组降容', '暴风穿越运行', '24016', 'msg', 'var_38795', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (98, 0, '机组降容', '风速面内波动大运行', '24017', 'msg', 'var_18000,var_18001,var_18002,var_18003,var_18004,var_18005', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (99, 0, '机组降容', '场级控制器异常运行', '24018', 'msg', 'var_28003', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (100, 0, '机组降容', '阵风运行', '24019', 'msg', 'var_23543,var_23544,var_23545', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (101, 0, '机组降容', '大湍流运行', '24020', 'msg', 'var_23542,var_23522,var_15098', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (102, 0, '机组降容', '风速快速上升运行', '24021', 'msg', 'var_101,var_102,var_103', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (103, 0, '机组降容', '箱变顶层油温高降容', '8003', 'alarm', 'var_3002', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (104, 0, '机组降容', '主轴承温度降容', '3007,3008', 'alarm', 'var_173,var_174', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (105, 0, '机组降容', '发电机绕组温度高降容', '5014,5021,5022,5049,5050,5051', 'alarm', 'var_206,var_207,var_208,var_209,var_210,var_211', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (106, 0, '机组降容', '齿轮箱轴承温度高', '1001,1003', 'alarm', 'var_171,var_172', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (107, 0, '机组降容', 'IPC降容', '13036,30004,30005,30006,30007,30008,30009,30010,30011,30012,30013,30014,30015,30016,30017,30018', 'alarm', 'var_1,winSpd,var_2704,var_2706,var_359,var_363,var_2709,rightYawSingle,leftYawSingle,var_407,var_409,var_382,var_383,var_94,genSpeed,var_15007,var_226,limitPowBool,var_246,var_51,var_998,var_1001,var_1002,workMode,var_18000,var_18001,var_18002,var_18003,var_18004,var_18005,var_18006,var_18007,var_18008,var_18009,var_18010,var_18011,var_18012,var_18013,var_18014,var_18015,var_18016,var_18017,var_18018,var_18019,var_18020,var_18021,var_18022,var_18023,var_18024,var_23569,var_101,var_102,var_103,var_18028,var_18029,var_18030,var_1686,var_110,var_111,var_112', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (108, 1, '叶片pitchkick', '叶片pitchkick', 'true', 'flag', 'var_101,var_102,var_103,var_246,var_94,var_23569', 'var_23569', 5, 'BladePitchkick');
INSERT INTO `turbine_fault_type` VALUES (109, 1, '叶片桨距角不同步', '叶片桨距角不同步', '4128', 'fault', 'var_101,var_102,var_103,var_18028,var_18029,var_18030', 'code', 5, 'BladeAsynchronous');
INSERT INTO `turbine_fault_type` VALUES (110, 1, '叶根载荷不平衡', '叶根载荷不平衡', NULL, NULL, 'var_382,var_18000,var_18001,var_18002,var_18003,var_18004,var_18005,var_18008,var_18009,var_18010,var_18011', '', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (111, 1, '风轮方位角异常', '风轮方位角异常', '3001730024', 'fault', 'var_18000,var_18006', 'code', 5, 'HubAzimuth');
INSERT INTO `turbine_fault_type` VALUES (112, 1, '叶根摆振弯矩超限', '叶根摆振弯矩超限', NULL, NULL, 'var_18000,var_18001,var_18002,var_18003,var_18004,var_18005,var_101,var_102,var_103,var_382,var_383', '', 5, 'BladeOverloaded');
INSERT INTO `turbine_fault_type` VALUES (113, 1, '叶根摆挥舞矩超限', '叶根摆挥舞矩超限', '3001130018', 'fault', 'var_18000,var_18001,var_18002,var_18003,var_18004,var_18005,var_101,var_102,var_103,var_382,var_383', 'code', 5, 'BladeOverloaded');
INSERT INTO `turbine_fault_type` VALUES (114, 1, '机组降容', '变流器1单模运行', '11120', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (115, 1, '机组降容', '变流器2单模运行', '11121', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (116, 1, '机组降容', '基于气象站的ECD保护运行', '24010', 'msg', 'var_38793,var_38794,var_2708', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (117, 1, '机组降容', '湍流超过设计运行', '24011', 'msg', 'var_38793', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (118, 1, '机组降容', '齿轮箱油池温度低运行', '24012', 'msg', 'var_175', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (119, 1, '机组降容', '风向偏差大运行', '24013', 'msg', 'var_1834', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (120, 1, '机组降容', '风速波动大运行', '24014', 'msg', 'var_101,var_102,var_103,var_226,var_18000,var_18001,var_18002,var_18003,var_18004,var_18005', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (121, 1, '机组降容', '变流器减载运行', '24015', 'msg', 'totalFaultBool', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (122, 1, '机组降容', '暴风穿越运行', '24016', 'msg', 'var_38795', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (123, 1, '机组降容', '风速面内波动大运行', '24017', 'msg', 'var_18000,var_18001,var_18002,var_18003,var_18004,var_18005', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (124, 1, '机组降容', '场级控制器异常运行', '24018', 'msg', 'var_28003', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (125, 1, '机组降容', '阵风运行', '24019', 'msg', 'var_23543,var_23544,var_23545', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (126, 1, '机组降容', '大湍流运行', '24020', 'msg', 'var_23542,var_23522,var_15098', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (127, 1, '机组降容', '风速快速上升运行', '24021', 'msg', 'var_101,var_102,var_103', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (128, 1, '机组降容', '箱变顶层油温高降容', '8003', 'alarm', 'var_3002', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (129, 1, '机组降容', '主轴承温度降容', '3007,3008', 'alarm', 'var_173,var_174', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (130, 1, '机组降容', '发电机绕组温度高降容', '5014,5021,5022,5049,5050,5051', 'alarm', 'var_206,var_207,var_208,var_209,var_210,var_211', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (131, 1, '机组降容', '齿轮箱轴承温度高', '1001,1003', 'alarm', 'var_171,var_172', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (132, 1, '机组降容', 'IPC降容', '13036,30004,30005,30006,30007,30008,30009,30010,30011,30012,30013,30014,30015,30016,30017,30018', 'alarm', 'var_1,winSpd,var_2704,var_2706,var_359,var_363,var_2709,rightYawSingle,leftYawSingle,var_407,var_409,var_382,var_383,var_94,genSpeed,var_15007,var_226,limitPowBool,var_246,var_51,var_998,var_1001,var_1002,workMode,var_18000,var_18001,var_18002,var_18003,var_18004,var_18005,var_18006,var_18007,var_18008,var_18009,var_18010,var_18011,var_18012,var_18013,var_18014,var_18015,var_18016,var_18017,var_18018,var_18019,var_18020,var_18021,var_18022,var_18023,var_18024,var_23569,var_101,var_102,var_103,var_18028,var_18029,var_18030,var_1686,var_110,var_111,var_112', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (133, 1, '变流器故障', '变流器1控制序列错误故障', '11002', 'fault', 'converterFaultCode,var_1758', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (134, 1, '变流器故障', '变流器1冷却液入口压力过高故障', '11005', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (135, 1, '变流器故障', '变流器1冷却液入口压力过低故障', '11006', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (136, 1, '变流器故障', '变流器1冷却液泵电机过载故障', '11015', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (137, 1, '变流器故障', '变流器1故障激活故障', '11017', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (138, 1, '变流器故障', '变流器1发电机速度传感器错误故障', '11018', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (139, 1, '变流器故障', '变流器1看门狗信号丢失故障', '11022', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (140, 1, '变流器故障', '变流器2冷却液入口压力过高故障', '11028', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (141, 1, '变流器故障', '变流器2冷却液入口压力过低故障', '11029', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (142, 1, '变流器故障', '变流器2冷却液泵电机过载故障', '11038', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (143, 1, '变流器故障', '变流器2故障激活故障', '11040', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (144, 1, '变流器故障', '变流器3冷却液入口压力过高故障', '11048', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (145, 1, '变流器故障', '变流器3冷却液入口压力过低故障', '11049', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (146, 1, '变流器故障', '变流器3冷却液泵电机过载故障', '11058', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (147, 1, '变流器故障', '变流器4冷却液入口压力过高故障', '11063', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (148, 1, '变流器故障', '变流器4冷却液入口压力过低故障', '11064', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (149, 1, '变流器故障', '变流器4冷却液泵电机过载故障', '11073', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007,var_15004,var_15005,var_15006,var_15009,var_15010,var_15011', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (150, 1, '变流器故障', '变流器通讯错误故障', '11076', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (151, 1, '变流器故障', '变流器通讯重新初始化故障', '11077', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (152, 1, '变流器故障', '变流器电源过载故障', '11078', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (153, 1, '变流器故障', '发电机机械速度太高故障', '11079', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (154, 1, '变流器故障', '发电机机械速度太低故障', '11080', 'fault', NULL, 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (155, 1, '变流器故障', '变流器LVRT激活故障', '11084', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (156, 1, '变流器故障', '变流器MCB跳闸', '11087', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (157, 1, '变流器故障', '变流器故障激活', '11088', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (158, 1, '变流器故障', '变流器1冷却液入口温度过高故障', '11009', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (159, 1, '变流器故障', '变流器1冷却液入口温度过低故障', '11010', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (160, 1, '变流器故障', '变流器1冷却风扇过载故障', '11016', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (161, 1, '变流器故障', '变流器1加热过载故障', '11019', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (162, 1, '变流器故障', '变流器2冷却液入口温度过高故障', '11032', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (163, 1, '变流器故障', '变流器2冷却液入口温度过低故障', '11033', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (164, 1, '变流器故障', '变流器2冷却风扇过载故障', '11039', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (165, 1, '变流器故障', '变流器3冷却液入口温度过高故障', '11052', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (166, 1, '变流器故障', '变流器3冷却风扇过载故障', '11059', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (167, 1, '变流器故障', '变流器3加热过载故障', '11060', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (168, 1, '变流器故障', '变流器4冷却液入口温度过高故障', '11067', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (169, 1, '变流器故障', '变流器4冷却液入口温度过低故障', '11068', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (170, 1, '变流器故障', '变流器4冷却风扇过载故障', '11074', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (171, 1, '变流器故障', '变流器4加热过载故障', '11075', 'fault', 'converterFaultCode,var_12015,var_12016,var_1758,var_15007', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (172, 1, '变流器故障', '变流器电网故障', '11092', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (173, 1, '变流器故障', '变流器直流母线电压故障', '11093', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (174, 1, '变流器故障', '变流器网侧模块电流故障', '11094', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (175, 1, '变流器故障', '变流器网侧模块硬件故障', '11095', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (176, 1, '变流器故障', '变流器温度高故障', '11096', 'fault', 'var_12016,converterFaultCode', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (177, 1, '变流器故障', '变流器机侧模块电流故障', '11097', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (178, 1, '变流器故障', '变流器机侧模块硬件故障', '11098', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (179, 1, '变流器故障', '变流器转速故障', '11099', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (180, 1, '变流器故障', '变流器定子电压故障', '11100', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (181, 1, '变流器故障', '变流器FRT故障', '11101', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (182, 1, '变流器故障', '变流器同步故障', '11102', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (183, 1, '变流器故障', '变流器主回路开关故障', '11103', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (184, 1, '变流器故障', '变流器接口故障', '11104', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (185, 1, '变流器故障', '变流器控制系统故障', '11105', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (186, 1, '变流器故障', '变流器chopper故障', '11106', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (187, 1, '变流器故障', '变流器其他故障', '11107', 'fault', 'converterFaultCode,var_15004,var_15005,var_15006,var_15007,var_15009,var_15010,var_15011,var_15012,var_15013,var_15014,var_15015', 'code', 5, 'ordinary');
INSERT INTO `turbine_fault_type` VALUES (188, 1, '后备电源故障', '后备电源故障', '31004', 'fault', 'var_18359、var_18360,var_18362,var_18363,var_18364', 'code', 5, 'ordinary');

-- ----------------------------
-- Table structure for turbine_model_points
-- ----------------------------
DROP TABLE IF EXISTS `turbine_model_points`;
CREATE TABLE `turbine_model_points`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `point_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `var_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '本地tdengine，set_id=20835的var_name，不变量',
  `datatype` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'F',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = 'tdengine的测点设置' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_model_points
-- ----------------------------
INSERT INTO `turbine_model_points` VALUES (1, '环境温度', 'evnTemp', 'F');
INSERT INTO `turbine_model_points` VALUES (2, '限功率运行状态', 'limitPowBool', 'B');
INSERT INTO `turbine_model_points` VALUES (3, '并网', 'onGrid', 'B');
INSERT INTO `turbine_model_points` VALUES (4, '有功功率', 'powAct', 'F');
INSERT INTO `turbine_model_points` VALUES (5, '无功功率', 'powReact', 'F');
INSERT INTO `turbine_model_points` VALUES (6, '故障', 'totalFaultBool', 'B');
INSERT INTO `turbine_model_points` VALUES (7, '1#叶片实际角度', 'var_101', 'F');
INSERT INTO `turbine_model_points` VALUES (8, '2#叶片实际角度', 'var_102', 'F');
INSERT INTO `turbine_model_points` VALUES (9, '3#叶片实际角度', 'var_103', 'F');
INSERT INTO `turbine_model_points` VALUES (10, '1#叶片变桨速度', 'var_107', 'F');
INSERT INTO `turbine_model_points` VALUES (11, '1#叶片变桨电机转矩', 'var_12031', 'F');
INSERT INTO `turbine_model_points` VALUES (12, '发电机转矩', 'var_226', 'F');
INSERT INTO `turbine_model_points` VALUES (13, '电网有功功率', 'var_246', 'F');
INSERT INTO `turbine_model_points` VALUES (14, '瞬时风向', 'var_363', 'F');
INSERT INTO `turbine_model_points` VALUES (15, '机舱X方向振动', 'var_382', 'F');
INSERT INTO `turbine_model_points` VALUES (16, '机舱Y方向振动', 'var_383', 'F');
INSERT INTO `turbine_model_points` VALUES (17, '偏航速度', 'var_407', 'F');
INSERT INTO `turbine_model_points` VALUES (18, '偏航角度', 'var_409', 'F');
INSERT INTO `turbine_model_points` VALUES (19, '偏航压力', 'var_412', 'F');
INSERT INTO `turbine_model_points` VALUES (20, '风轮转速', 'var_94', 'F');
INSERT INTO `turbine_model_points` VALUES (21, '瞬时风速', 'winSpd', 'F');
INSERT INTO `turbine_model_points` VALUES (22, '工作模式', 'workMode', 'I');

-- ----------------------------
-- Table structure for turbine_operation_mode
-- ----------------------------
DROP TABLE IF EXISTS `turbine_operation_mode`;
CREATE TABLE `turbine_operation_mode`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` int NOT NULL,
  `descrption` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '风机运行模式' ROW_FORMAT = DYNAMIC;

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
-- Table structure for turbine_outlier_monitor
-- ----------------------------
DROP TABLE IF EXISTS `turbine_outlier_monitor`;
CREATE TABLE `turbine_outlier_monitor`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `system` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '部件名',
  `type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '温度 or 载荷',
  `var_names` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '要监控的变量名；逗号分割',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of turbine_outlier_monitor
-- ----------------------------
INSERT INTO `turbine_outlier_monitor` VALUES (1, '叶片', '温度', 'var_126,var_116,var_113,var_15032,var_15035,var_127,var_117,var_114,var_15033,var_15036,var_128,var_118,var_115,var_15034,var_15037');
INSERT INTO `turbine_outlier_monitor` VALUES (2, 'IGBT', '温度', 'var_15041');
INSERT INTO `turbine_outlier_monitor` VALUES (3, '传动系统', '温度', 'var_15041,var_38826,var_173,var_174,var_171,var_172,var_175');
INSERT INTO `turbine_outlier_monitor` VALUES (4, '发电机', '温度', 'var_213,var_2763,var_2761,var_2762,var_222,var_223,var_206,var_207,var_208,var_209,var_210,var_211');
INSERT INTO `turbine_outlier_monitor` VALUES (5, '变压器', '温度', 'var_1721,var_1722,var_1723,var_1724,var_2697');
INSERT INTO `turbine_outlier_monitor` VALUES (6, '变流器', '温度', 'var_12016');
INSERT INTO `turbine_outlier_monitor` VALUES (7, '后备电源柜', '温度', 'var_18361');
INSERT INTO `turbine_outlier_monitor` VALUES (8, '塔基', '温度', 'var_425,var_1769,var_1159,var_2696');
INSERT INTO `turbine_outlier_monitor` VALUES (9, '机舱', '温度', 'var_1644,var_380,var_1767,var_1768,var_372,evnTemp');
INSERT INTO `turbine_outlier_monitor` VALUES (10, '轮毂', '温度', 'var_1004');
INSERT INTO `turbine_outlier_monitor` VALUES (11, '叶片', '载荷', 'var_18003,var_18000,var_18004,var_18001,var_18005,var_18002');

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
  INDEX `set_id`(`set_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 43 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '风机部件关键参数故障阈值' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of turbine_variable_bound
-- ----------------------------
INSERT INTO `turbine_variable_bound` VALUES (1, '20835', 'var_171', '齿轮箱HS1轴承温度', -999.999, 95);
INSERT INTO `turbine_variable_bound` VALUES (2, '20835', 'var_172', '齿轮箱HS2轴承温度', -999.999, 95);
INSERT INTO `turbine_variable_bound` VALUES (3, '20835', 'var_175', '齿轮箱油池温度', -100, 75);
INSERT INTO `turbine_variable_bound` VALUES (4, '20835', 'var_182', '齿轮箱进口压力', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (5, '20835', 'var_2713', '齿轮箱过滤器1压差', -999.999, 3);
INSERT INTO `turbine_variable_bound` VALUES (6, '20835', 'var_2714', '齿轮箱过滤器2压差', -999.999, 3);
INSERT INTO `turbine_variable_bound` VALUES (7, '20835', 'var_2715', '齿轮箱过滤器3压差', -999.999, 3);
INSERT INTO `turbine_variable_bound` VALUES (8, '20835', 'var_104', '1#叶片冗余变桨角度', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (9, '20835', 'var_105', '2#叶片冗余变桨角度', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (10, '20835', 'abs(var_171-var_172)', '前后主轴承温绝对差', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (11, '20835', 'abs(var_104-var_105)', '1#-2#叶片角度绝对差', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (12, '20835', 'var_206', '发电机绕组u1温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (13, '20835', 'var_207', '发电机绕组u2温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (14, '20835', 'var_208', '发电机绕组v1温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (15, '20835', 'var_209', '发电机绕组v2温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (16, '20835', 'var_210', '发电机绕组w1温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (17, '20835', 'var_211', '发电机绕组w2温度', -999.999, 155);
INSERT INTO `turbine_variable_bound` VALUES (18, '20835', 'var_106', '3#叶片冗余变桨角度', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (19, '20835', 'abs(var_104-var_106)', '1#-3#叶片角度绝对差', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (20, '20835', 'abs(var_105-var_106)', '2#-3#叶片角度绝对差', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (21, '20835', 'var_15004', '变流器机侧A相电流', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (22, '20835', 'var_15005', '变流器机侧B相电流', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (23, '20835', 'var_15006', '变流器机侧C相电流', -999.999, 100);
INSERT INTO `turbine_variable_bound` VALUES (24, '20835', 'var_12016', '变流器入水口温度反馈', -10, 60);
INSERT INTO `turbine_variable_bound` VALUES (25, '20835', 'var_18000', '叶根载荷监测叶片1摆振弯矩', -23000000, 23000000);
INSERT INTO `turbine_variable_bound` VALUES (26, '20835', 'var_18001', '叶根载荷监测叶片2摆振弯矩', -23000000, 23000000);
INSERT INTO `turbine_variable_bound` VALUES (27, '20835', 'var_18002', '叶根载荷监测叶片3摆振弯矩', -23000000, 23000000);
INSERT INTO `turbine_variable_bound` VALUES (28, '20835', 'var_18003', '叶根载荷监测叶片1挥舞弯矩', -4500000, 42000000);
INSERT INTO `turbine_variable_bound` VALUES (29, '20835', 'var_18004', '叶根载荷监测叶片2挥舞弯矩', -4500000, 42000000);
INSERT INTO `turbine_variable_bound` VALUES (30, '20835', 'var_18005', '叶根载荷监测叶片3挥舞弯矩', -4500000, 42000000);
INSERT INTO `turbine_variable_bound` VALUES (31, '20835', 'var_246', '电网有功功率', -999.999, 9185);
INSERT INTO `turbine_variable_bound` VALUES (32, '20835', 'abs(avg(var_18003)-avg(var_18004))', '1#-2#叶片挥舞弯矩差', -999.999, 4500000);
INSERT INTO `turbine_variable_bound` VALUES (33, '20835', 'abs(avg(var_18003)-avg(var_18005))', '1#-3#叶片挥舞弯矩差', -999.999, 4500000);
INSERT INTO `turbine_variable_bound` VALUES (34, '20835', 'abs(avg(var_18004)-avg(var_18005))', '2#-3#叶片挥舞弯矩差', -999.999, 4500000);
INSERT INTO `turbine_variable_bound` VALUES (35, '20835', 'abs(avg(var_18000)-avg(var_18001))', '1#-2#叶片摆振弯矩差', -999.999, 2000000);
INSERT INTO `turbine_variable_bound` VALUES (36, '20835', 'abs(avg(var_18000)-avg(var_18002))', '1#-3#叶片摆振弯矩差', -999.999, 2000000);
INSERT INTO `turbine_variable_bound` VALUES (37, '20835', 'abs(avg(var_18001)-avg(var_18002))', '2#-3#叶片摆振弯矩差', -999.999, 2000000);
INSERT INTO `turbine_variable_bound` VALUES (38, '20835', 'blade_flapwise', '叶根挥舞弯矩', -4500000, 42000000);
INSERT INTO `turbine_variable_bound` VALUES (39, '20835', 'blade_edgewise', '叶根摆振弯矩', -23000000, 23000000);
INSERT INTO `turbine_variable_bound` VALUES (40, '20835', 'blade_flapwise_diff', '不平衡叶根挥舞弯矩', -4500000, 4500000);
INSERT INTO `turbine_variable_bound` VALUES (41, '20835', 'blade_edgewise_diff', '不平衡叶根摆振弯矩', -2500000, 2500000);
INSERT INTO `turbine_variable_bound` VALUES (42, '20835', 'blade_asynchronous', '变桨角度不一致', -7.5, 7.5);

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
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统用户' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'admin', 'pbkdf2:sha256:260000$OBcshGdRulbnvt65$db230312eee30c161807a67f25cb6b2dbcb83b5f36d654b6379c54fc8336bfd9', 1);

-- ----------------------------
-- Table structure for windfarm_configuration
-- ----------------------------
DROP TABLE IF EXISTS `windfarm_configuration`;
CREATE TABLE `windfarm_configuration`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `set_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `gearbox_ratio` float NOT NULL DEFAULT 107,
  `is_offshore` int NOT NULL COMMENT '1=海上风机，0=陆上风机',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of windfarm_configuration
-- ----------------------------
INSERT INTO `windfarm_configuration` VALUES (1, '20835', 107, 1);
INSERT INTO `windfarm_configuration` VALUES (2, '20080', 107, 0);

SET FOREIGN_KEY_CHECKS = 1;
