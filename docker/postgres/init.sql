-- PostgreSQL initialization script for VMLab
-- This script will be executed when the PostgreSQL container starts for the first time

-- 创建数据库扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 设置时区
SET timezone = 'UTC';

-- 创建用户和数据库的权限已经在环境变量中设置了
-- 这里可以添加其他初始化语句
