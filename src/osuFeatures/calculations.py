async def gradeCalculator(*, n300: int = 0, n100: int = 0, n50: int = 0, miss: int = 0):
    objectCount = n300 + n100 + n50 + miss

    if objectCount == n300:
        return 'SS'
    if 100/objectCount*n300 > 90 and 100/objectCount*n50 < 1 and miss == 0:
        return 'S'
    if (100 / objectCount * n300 > 90) or (100 / objectCount * n300 > 80 and miss == 0):
        return 'A'
    if (100 / objectCount * n300 > 80) or (100 / objectCount * n300 > 70 and miss == 0):
        return 'B'
    if 100 / objectCount * n300 > 60:
        return 'C'

    return 'D'

