# import time
# starttime = time.time()
# while True:
#     print(time.time())
#     time.sleep(0.01 - ((time.time() - starttime) % 0.01))
deadzone_upper = 127
deadzone_lower = 123


def diff_from_deadzone(x, y):
    if x <= deadzone_lower or x >= deadzone_upper or y <= deadzone_lower or y >= deadzone_upper:
        relX = min(0, x - deadzone_lower) if x <= deadzone_lower else max(0, x - deadzone_upper)
        relY = min(0, y - deadzone_lower) if y <= deadzone_lower else max(0, y - deadzone_upper)
        return (relX, relY)
    return (0, 0)

print(diff_from_deadzone(125, 125))
print(diff_from_deadzone(123, 127))
print(diff_from_deadzone(128, 128))
print(diff_from_deadzone(122, 122))
print(diff_from_deadzone(130, 130))
print(diff_from_deadzone(125, 130))
print(diff_from_deadzone(121, 129))
print(diff_from_deadzone(129, 121))
print(diff_from_deadzone(121, 121))


