import threading
import queue
import numpy as np
from .cv import img_str


def recognition(image) -> str:

    # required81 = ("412307564"*9)
    required81 = "110000300000900082500000000400020007000709000280000060000006500023810000070200000"
    # time.sleep(2)
    lst = img_str(image)
    required81 = ''.join(map(str, lst))
    print(required81, 'rec')

    return required81

# **************solving phase*********************


def check(array, row, col, num):
    if num in array[:, col]:
        return False
    elif num in array[row, :]:
        return False
    elif num in array[((row//3)*3):((row//3)*3)+3,
                      ((col//3)*3): ((col//3)*3)+3]:
        return False
    else:
        return True


def not_twice(array, row, col, num):
    test_arr = [array[:, col], array[row, :],
                array[((row//3)*3):((row//3)*3)+3,
                      ((col//3)*3): ((col//3)*3)+3]]
    ans = []
    for arr in test_arr:
        ans += [arr.flatten().tolist().count(num) == 1]
    return all(ans)


def validity(list81):
    array = np.array(list81).reshape(9, 9).astype(int)
    result = []
    for row in range(9):
        for col in range(9):
            if array[row, col] != 0:
                num = array[row, col]
                result += [not_twice(array, row, col, num)]
    return all(result)


def coordinates_l(array):
    coords = []
    for row in range(9):
        for col in range(9):
            if array[row, col] == 0:
                coords += [(row, col)]
    return coords


def process(list81, q):
    array = np.array(list81).reshape(9, 9).astype(int)

    def solved(array):
        coords = coordinates_l(array)
    #     print(coords)
        if coords == []:
            return True
        else:
            for coord in coords:
                r, c = coord

                for num in range(1, 10):
                    if check(array, r, c, num):
                        #                 print(r,c,num)
                        array[r, c] = num
                        if solved(array):
                            return True
                        array[r, c] = 0
                return False
    solved(array)
    q.put(array)


def solve(list81):
    q = queue.Queue()
    t1 = threading.Thread(target=process, args=(list81, q))
    t1.start()
    t1.join(120)
    if t1.is_alive():
        return True  # timeout
    sol_list = q.get().flatten().tolist()
    return ''.join(map(str, sol_list))
