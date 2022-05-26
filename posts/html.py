
from typing import Iterable


def construct(sudokustr, solutionstr) -> str:
    """takes sudoku-string & solution string to make presentable html 9x9-grid"""
    div = '<div class="grid"><span>'
    for i in range(9):
        for j in range(9):
            val = sudokustr[i*9: (i+1)*9][j]
            klass = 'cell'
            if val == '0':
                val = solutionstr[i*9: (i+1)*9][j]
                klass = 'empty-cell'
            cell = f'<input id="cell{i}{j}" class="{klass}" name="array81" value="{val}" readonly maxlength="1" inputmode="numeric" pattern="^[1-9]$" title="read-only" min="1" size="1" />'
            div += cell
        div += '</span><br/>'
    div += '</div>'
    return div


class Custom_obj:
    """ from SudokuModel Queryset obj -> Obj with extra attributes"""
    def __init__(self, in_obj):
        self.name = in_obj.name
        self.story = in_obj.story
        self.id = in_obj.id
        self.name_short = in_obj.name_short
        self.show_time = in_obj.show_time
        self.author = in_obj.author
        self.div = construct(in_obj.sudokustr, in_obj.solutionstr)


class My_Queryset(Iterable):
    """takes a django Queryset-object -> 
    Iterable of newly defined custom-objects
    (which are modified version of model objects contained in the Queryset-object)"""

    def __init__(self, qs):
        self.qs = qs
        return super().__init__()

    def __iter__(self):
        return iter(Custom_obj(each) for each in self.qs)
