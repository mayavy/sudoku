
from django.shortcuts import get_object_or_404, redirect, render
# from django.core.files.storage import default_storage
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required

from .utils import recognition, validity, solve
from .models import SudokuModel, CommentModel
from .html import construct, My_Queryset, Custom_obj


def about_view(request, *args, **kwargs):
    return render(request, 'sudoku/about.html')


@login_required
def sudoku_list_view(request, *args, **kwargs):
    qs = SudokuModel.objects.all()
    context = {'qs': My_Queryset(qs)}  # todo login redirect issue !!!

    return render(request, 'sudoku/sudokulist.html', context)


@login_required
def sudoku_detail_view(request, *args, **kwargs):
    if request.method == 'GET':
        pk = kwargs['pk']
        sudoku_obj = get_object_or_404(SudokuModel, pk=pk)

        commentqs = CommentModel.objects.filter(
            parentsudoku=pk).order_by('-datecreated')
        context = {'post': Custom_obj(sudoku_obj), 'commentqs': commentqs}
        return render(request, 'sudoku/sudokudetail.html', context)

    elif request.method == 'POST':
        pk = kwargs['pk']
        comment = request.POST['comment']
        parent = SudokuModel.objects.get(pk=pk)
        author = request.user
        CommentModel.objects.create(
            comment=comment, parentsudoku=parent, author=author)
        return redirect(request.path, *args, **kwargs)
    else:
        return HttpResponseBadRequest('what ? 404 ')


def home_view(request, *args, **kwargs):
    # 1/3
    if request.method == 'GET':
        return render(request, 'sudoku/home.html')
    # 2/3
    elif request.method == 'POST':
        print('post')
        if 'imagefile' in request.FILES and request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            file = request.FILES["imagefile"]
            # file = default_storage.save(file.name, file)
            # recognition

            string81 = recognition(file)

            return JsonResponse({"string81": string81,  'recognised': True}, status=200)
        elif 'imagefile' not in request.FILES:
            print(request.POST, 'post req')
            list81 = request.POST.getlist('array81')[:81]
            string81 = ''.join(map(str, list81))
            timeout = False

            invalid = not(validity(list81))

            if not invalid:
                solution = solve(list81)
                print(solution)
                if type(solution) == str and ('0' not in solution):

                    # now solved, saving data !
                    if request.user.is_authenticated:
                        story = request.POST.get('story')
                        name = request.POST.get('name')
                        SudokuModel.objects.create(author=request.user, sudokustr=string81, story=story,
                                                   name=name, solutionstr=solution)
                    string81 = solution
                else:
                    # timeout = solution  # timeout
                    timeout = True

            return JsonResponse({'string81': string81, 'invalid': invalid, 'timeout': timeout}, status=200)
        else:
            return JsonResponse({'error': 'Error occured-400'}, status=400)
    # 3/3
    else:
        return HttpResponseBadRequest('what ? 404 ')
