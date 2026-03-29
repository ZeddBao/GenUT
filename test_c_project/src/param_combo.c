/**
 * @file param_combo.c
 * @brief 参数组合测试 - 实现各种参数组合测试场景，用于单元测试生成
 *
 * 本文件实现参数组合测试的示例函数，涵盖：
 * 1. 边界值分析：最小值、最大值、刚好超出
 * 2. 等价类划分：同一等价类代表性值
 * 3. 组合测试：多参数组合覆盖
 * 4. 正交数组：减少测试用例数
 */

#include "param_combo.h"

/* ==================== 边界值分析 ==================== */

int boundary_value_analysis_single(int value)
{
    // 测试单个参数的边界值
    const int MIN_VALID = 0;
    const int MAX_VALID = 100;

    if (value < MIN_VALID) {
        return -1; // 低于最小值
    } else if (value == MIN_VALID) {
        return 0; // 最小值
    } else if (value > MIN_VALID && value < MAX_VALID) {
        return 1; // 正常范围（内部值）
    } else if (value == MAX_VALID) {
        return 2; // 最大值
    } else { // value > MAX_VALID
        return 3; // 高于最大值
    }
}

int boundary_value_analysis_double(int a, int b)
{
    // 测试两个参数的边界值组合
    const int MIN = 0;
    const int MAX = 10;

    int result = 0;

    // 检查第一个参数的边界
    if (a < MIN) {
        result |= 0x01; // a低于最小值
    } else if (a == MIN) {
        result |= 0x02; // a等于最小值
    } else if (a > MIN && a < MAX) {
        result |= 0x04; // a在正常范围内
    } else if (a == MAX) {
        result |= 0x08; // a等于最大值
    } else { // a > MAX
        result |= 0x10; // a高于最大值
    }

    // 检查第二个参数的边界
    if (b < MIN) {
        result |= 0x20; // b低于最小值
    } else if (b == MIN) {
        result |= 0x40; // b等于最小值
    } else if (b > MIN && b < MAX) {
        result |= 0x80; // b在正常范围内
    } else if (b == MAX) {
        result |= 0x100; // b等于最大值
    } else { // b > MAX
        result |= 0x200; // b高于最大值
    }

    return result;
}

int boundary_value_analysis_triple(int x, int y, int z)
{
    // 测试三个参数的边界值组合
    const int MIN = -10;
    const int MAX = 10;

    int score = 0;

    // 检查每个参数是否在有效范围内
    if (x >= MIN && x <= MAX) score += 1;
    if (y >= MIN && y <= MAX) score += 2;
    if (z >= MIN && z <= MAX) score += 4;

    // 检查边界情况
    if (x == MIN || x == MAX) score += 8;
    if (y == MIN || y == MAX) score += 16;
    if (z == MIN || z == MAX) score += 32;

    // 检查刚好超出边界的情况
    if (x == MIN - 1 || x == MAX + 1) score += 64;
    if (y == MIN - 1 || y == MAX + 1) score += 128;
    if (z == MIN - 1 || z == MAX + 1) score += 256;

    return score;
}

/* ==================== 等价类划分 ==================== */

int equivalence_class_age(int age)
{
    // 年龄等价类划分
    if (age < 0) {
        return -1; // 无效年龄
    } else if (age >= 0 && age <= 12) {
        return 0; // 儿童
    } else if (age >= 13 && age <= 17) {
        return 1; // 青少年
    } else if (age >= 18 && age <= 64) {
        return 2; // 成人
    } else { // age >= 65
        return 3; // 老年
    }
}

int equivalence_class_score(int score)
{
    // 成绩等价类划分
    if (score < 0 || score > 100) {
        return -1; // 无效分数
    } else if (score < 60) {
        return 0; // F
    } else if (score < 70) {
        return 1; // D
    } else if (score < 80) {
        return 2; // C
    } else if (score < 90) {
        return 3; // B
    } else { // score >= 90
        return 4; // A
    }
}

int equivalence_class_temperature(int temperature)
{
    // 温度等价类划分
    if (temperature < -20) {
        return 0; // 冰冻
    } else if (temperature >= -20 && temperature < 0) {
        return 1; // 寒冷
    } else if (temperature >= 0 && temperature < 15) {
        return 2; // 凉爽
    } else if (temperature >= 15 && temperature < 30) {
        return 3; // 温暖
    } else { // temperature >= 30
        return 4; // 炎热
    }
}

/* ==================== 组合测试 ==================== */

int two_factor_combinatorial(bool flag1, bool flag2)
{
    // 两因素组合测试（布尔值）
    int result = 0;

    if (flag1 && flag2) {
        result = 0; // 两个都为真
    } else if (flag1 && !flag2) {
        result = 1; // 第一个真，第二个假
    } else if (!flag1 && flag2) {
        result = 2; // 第一个假，第二个真
    } else { // !flag1 && !flag2
        result = 3; // 两个都为假
    }

    return result;
}

int three_factor_combinatorial(int mode, int priority, bool enabled)
{
    // 三因素组合测试
    int score = 0;

    // 模式组合
    switch (mode) {
        case 0:
            score += 0; // 模式0
            break;
        case 1:
            score += 10; // 模式1
            break;
        case 2:
            score += 20; // 模式2
            break;
        case 3:
            score += 30; // 模式3
            break;
        default:
            score += 100; // 无效模式
            break;
    }

    // 优先级组合
    switch (priority) {
        case 0:
            score += 0; // 低优先级
            break;
        case 1:
            score += 1; // 中优先级
            break;
        case 2:
            score += 2; // 高优先级
            break;
        default:
            score += 10; // 无效优先级
            break;
    }

    // 启用状态组合
    if (enabled) {
        score += 1000; // 启用
    } else {
        score += 2000; // 禁用
    }

    return score;
}

int multi_factor_combinatorial(int timeout, int retries, int buffer_size, bool use_ssl)
{
    // 多因素组合测试
    int rating = 0;

    // 超时评分
    if (timeout == 0) {
        rating += 1; // 无超时
    } else if (timeout == 1) {
        rating += 2; // 短超时
    } else if (timeout == 2) {
        rating += 3; // 中超时
    } else if (timeout == 3) {
        rating += 4; // 长超时
    } else {
        rating += 0; // 无效超时
    }

    // 重试次数评分
    if (retries == 0) {
        rating += 10; // 不重试
    } else if (retries == 1) {
        rating += 20; // 重试1次
    } else if (retries == 2) {
        rating += 30; // 重试2次
    } else {
        rating += 0; // 无效重试次数
    }

    // 缓冲区大小评分
    if (buffer_size == 0) {
        rating += 100; // 小缓冲区
    } else if (buffer_size == 1) {
        rating += 200; // 中缓冲区
    } else if (buffer_size == 2) {
        rating += 300; // 大缓冲区
    } else {
        rating += 0; // 无效缓冲区大小
    }

    // SSL使用评分
    if (use_ssl) {
        rating += 1000; // 使用SSL
    } else {
        rating += 2000; // 不使用SSL
    }

    return rating;
}

/* ==================== 正交数组测试 ==================== */

int orthogonal_array_l4(int factor1, int factor2, int factor3)
{
    // L4(2^3)正交表测试
    // 正交表：
    // 1: 0 0 0
    // 2: 0 1 1
    // 3: 1 0 1
    // 4: 1 1 0

    int result = 0;

    // 检查是否匹配正交表中的某一行
    if (factor1 == 0 && factor2 == 0 && factor3 == 0) {
        result = 1; // 匹配第1行
    } else if (factor1 == 0 && factor2 == 1 && factor3 == 1) {
        result = 2; // 匹配第2行
    } else if (factor1 == 1 && factor2 == 0 && factor3 == 1) {
        result = 3; // 匹配第3行
    } else if (factor1 == 1 && factor2 == 1 && factor3 == 0) {
        result = 4; // 匹配第4行
    } else {
        result = 0; // 不匹配任何行
    }

    return result;
}

int orthogonal_array_l9(int level1, int level2, int level3)
{
    // L9(3^4)正交表测试（只使用前3个因素）
    // 正交表（简化，只显示前3列）：
    // 1: 0 0 0
    // 2: 0 1 1
    // 3: 0 2 2
    // 4: 1 0 1
    // 5: 1 1 2
    // 6: 1 2 0
    // 7: 2 0 2
    // 8: 2 1 0
    // 9: 2 2 1

    // 检查每个参数的有效范围
    if (level1 < 0 || level1 > 2 ||
        level2 < 0 || level2 > 2 ||
        level3 < 0 || level3 > 2) {
        return -1; // 无效参数
    }

    // 检查是否匹配正交表中的某一行
    if (level1 == 0 && level2 == 0 && level3 == 0) return 1;
    if (level1 == 0 && level2 == 1 && level3 == 1) return 2;
    if (level1 == 0 && level2 == 2 && level3 == 2) return 3;
    if (level1 == 1 && level2 == 0 && level3 == 1) return 4;
    if (level1 == 1 && level2 == 1 && level3 == 2) return 5;
    if (level1 == 1 && level2 == 2 && level3 == 0) return 6;
    if (level1 == 2 && level2 == 0 && level3 == 2) return 7;
    if (level1 == 2 && level2 == 1 && level3 == 0) return 8;
    if (level1 == 2 && level2 == 2 && level3 == 1) return 9;

    return 0; // 不匹配（理论上不会到达这里）
}