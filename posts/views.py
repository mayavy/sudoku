
from django.http import HttpResponseBadRequest, JsonResponse

from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import recognition, validity, solve
from .models import SudokuModel, CommentModel
from .html import construct, My_Queryset, Custom_obj


class AboutView(TemplateView):
    template_name = "sudoku/about.html"

class SudokuListView(LoginRequiredMixin, ListView):
    model = SudokuModel
    template_name = 'sudoku/sudokulist.html'
    context_object_name = 'qs'

    def get_queryset(self):
        qs = SudokuModel.objects.filter(author__is_active = True)
        my_qs = My_Queryset(qs)
        return my_qs


class SudokuDetailView(LoginRequiredMixin, DetailView):
    model = SudokuModel
    context_object_name = 'post'
    template_name = 'sudoku/sudokudetail.html'

    def get_object(self):
        return Custom_obj(super().get_object())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['commentqs'] = CommentModel.objects.filter(author__is_active = True).filter(
            parentsudoku=self.kwargs['pk']).order_by('-datecreated')
        return context

    def post(self, request, *args, **kwargs):
        comment = request.POST['comment']
        parent = super().get_object()
        author = request.user
        CommentModel.objects.create(comment = comment,
                parentsudoku = parent, author = author)
        return super().get(request, *args, **kwargs)

class HomeView(TemplateView):
    template_name = "sudoku/home.html"
    def post(self, request, *args, **kwargs):
        print('post')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if 'imagefile' in request.FILES:
                file = request.FILES["imagefile"]
                # file = default_storage.save(file.name, file)
                # recognition
                string81 = recognition(file)
                return JsonResponse({"string81": string81,  'recognised': True}, status=200)
            else:
                list81 = request.POST.getlist('array81')[:81]
                string81 = ''.join(map(str, list81))
                timeout = False
                valid = validity(list81)
                if valid:
                    solution = solve(list81)
                    print(solution)
                    if solution and ('0' not in solution):

                        # solved, now  saving data !
                        if request.user.is_authenticated:
                            story = request.POST.get('story')
                            name = request.POST.get('name')
                            SudokuModel.objects.create(author=request.user, sudokustr=string81,
                             story=story, name=name, solutionstr=solution)
                        string81 = solution
                    else:
                          # timeout
                        timeout = True

                return JsonResponse({'string81': string81, 'valid': valid, 'timeout': timeout}, status=200)
        else:
            return HttpResponseBadRequest('what ? 404 ')


        



