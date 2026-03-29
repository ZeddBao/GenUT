/**
 * @file param_combo.h
 * @brief 参数组合测试 - 演示各种参数组合测试场景，用于单元测试生成
 *
 * 本头文件包含参数组合测试的示例函数声明，涵盖：
 * 1. 边界值分析：最小值、最大值、刚好超出
 * 2. 等价类划分：同一等价类代表性值
 * 3. 组合测试：多参数组合覆盖
 * 4. 正交数组：减少测试用例数
 */

#ifndef PARAM_COMBO_H
#define PARAM_COMBO_H

#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ==================== 边界值分析 ==================== */

/**
 * @brief 边界值分析测试：单参数边界
 * @param value 输入值，测试边界：最小值、最大值、刚好超出
 * @return 根据边界条件返回不同的结果
 */
int boundary_value_analysis_single(int value);

/**
 * @brief 边界值分析测试：双参数边界
 * @param a 第一个参数
 * @param b 第二个参数
 * @return 根据边界条件组合返回结果
 */
int boundary_value_analysis_double(int a, int b);

/**
 * @brief 边界值分析测试：三参数边界
 * @param x X坐标
 * @param y Y坐标
 * @param z Z坐标
 * @return 根据三维边界条件返回结果
 */
int boundary_value_analysis_triple(int x, int y, int z);

/* ==================== 等价类划分 ==================== */

/**
 * @brief 等价类划分测试：年龄分类
 * @param age 年龄
 * @return 年龄分类：0-儿童，1-青少年，2-成人，3-老年
 */
int equivalence_class_age(int age);

/**
 * @brief 等价类划分测试：成绩等级
 * @param score 分数
 * @return 成绩等级：0-F，1-D，2-C，3-B，4-A
 */
int equivalence_class_score(int score);

/**
 * @brief 等价类划分测试：温度范围
 * @param temperature 温度（摄氏度）
 * @return 温度分类：0-冰冻，1-寒冷，2-凉爽，3-温暖，4-炎热
 */
int equivalence_class_temperature(int temperature);

/* ==================== 组合测试 ==================== */

/**
 * @brief 两因素组合测试：布尔参数组合
 * @param flag1 第一个标志
 * @param flag2 第二个标志
 * @return 组合结果编码
 */
int two_factor_combinatorial(bool flag1, bool flag2);

/**
 * @brief 三因素组合测试：模式选择
 * @param mode 模式（0-3）
 * @param priority 优先级（0-2）
 * @param enabled 是否启用
 * @return 组合结果
 */
int three_factor_combinatorial(int mode, int priority, bool enabled);

/**
 * @brief 多因素组合测试：配置参数
 * @param timeout 超时时间（0-3）
 * @param retries 重试次数（0-2）
 * @param buffer_size 缓冲区大小（0-2）
 * @param use_ssl 是否使用SSL
 * @return 配置评分
 */
int multi_factor_combinatorial(int timeout, int retries, int buffer_size, bool use_ssl);

/* ==================== 正交数组测试 ==================== */

/**
 * @brief 正交数组测试：L4(2^3)正交表
 * @param factor1 因素1（0或1）
 * @param factor2 因素2（0或1）
 * @param factor3 因素3（0或1）
 * @return 正交组合结果
 */
int orthogonal_array_l4(int factor1, int factor2, int factor3);

/**
 * @brief 正交数组测试：L9(3^4)正交表（只使用3个因素）
 * @param level1 因素1水平（0、1或2）
 * @param level2 因素2水平（0、1或2）
 * @param level3 因素3水平（0、1或2）
 * @return 正交组合结果
 */
int orthogonal_array_l9(int level1, int level2, int level3);

#ifdef __cplusplus
}
#endif

#endif /* PARAM_COMBO_H */