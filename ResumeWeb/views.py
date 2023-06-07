# Импорты
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import redirect
from django.shortcuts import render

from ResumeBot.management import functions as func
from .forms import CrResumeForm, UpdResumeForm, ChseSrchForm, ChseTyForm, UserRegisterForm
from .models import Resume


# Представления
# Все функции в этом файле обрабатывают html страницы или так называемые шаблоны,
# принимая от них данные через Post и Get запросы

# Представление главной страницы
def start(request):
    return render(request, 'index.html')


# Представление создания резюме
@login_required
def crresume(request):
    creator = request.user
    if Resume.objects.filter(user_id=creator.id).exists() and not creator.is_staff:
        return redirect('homepage')
    else:
        if request.method == "POST":
            if not Resume.objects.filter(user_id=creator.id).exists():
                form = CrResumeForm(request.POST, request.FILES)
                if form.is_valid():
                    res = form.save(commit=False)
                    res.user_id = creator.id
                    res.save()
                    group1 = Group.objects.get(name="Guests")
                    group2 = Group.objects.get(name="Interns")
                    if creator.groups.filter(name="Guests"):
                        group2.user_set.add(creator)
                        group1.user_set.remove(creator)

                    return redirect('homepage')
            else:
                return redirect('homepage')
        else:
            form = CrResumeForm
        return render(request, 'create.html', {'form': form})


# Представление просмотра резюме
@login_required
def shresume(request):
    creator = request.user
    if Resume.objects.filter(user_id=creator.id).exists() or creator.is_staff:
        fm = ChseSrchForm(request.POST or None)
        fm2 = ChseTyForm(request.POST)
        chses = None
        resumesfull = None
        resumes = None
        resumespart = None
        did = None
        done = "0"

        if request.POST.get('choose'):
            choose = request.POST.get('choose')
            if choose == "1":
                chses = "1"
            elif choose == "2":
                chses = "2"
            elif choose == "3":
                chses = "3"
            elif choose == "0":
                chses = "0"
                resumespart = Resume.objects.all()
                for image in resumespart:
                    image.birthday, image.grade, image.institution, image.curator, image.spec, image.skills, \
                    image.projects, image.project_links, image.education, image.first_lang, image.other_lang, \
                    image.country, image.pract_name, image.pract_period_from, image.pract_period_to, image.pract_jobs, \
                    image.linkedin, image.pract_tasks = None, None, None, None, None, None, None, None, None, None, None, \
                                                        None, None, None, None, None, None, None
                done = "1"
                did = 1
        if request.POST.get('srchph'):
            if chses == "1":
                search = request.POST.get('srchph')
                if search.startswith("7"):
                    search = "+" + search
                if Resume.objects.filter(phonenum=search).exists():
                    resumesfull = Resume.objects.filter(phonenum=search)
                    done = "1"
                did = 1
        if request.POST.get('srchla'):
            if chses == "2":
                search = request.POST.get('srchla')
                if search == "on":
                    search = "True"
                elif search == "off":
                    search = "False"
                if Resume.objects.filter(laptop=search).exists():
                    resumespart = Resume.objects.filter(laptop=search)
                    for image in resumespart:
                        image.birthday, image.grade, image.institution, image.curator, image.spec, image.skills, \
                        image.projects, image.project_links, image.education, image.first_lang, image.other_lang, \
                        image.country, image.pract_name, image.pract_period_from, image.pract_period_to, image.pract_jobs, \
                        image.linkedin, image.pract_tasks = None, None, None, None, None, None, None, None, None, None, None, \
                                                            None, None, None, None, None, None, None

                    done = "1"
                did = 1
        if request.POST.get('srchty'):
            if chses == "3":
                search = request.POST.get('srchty')
                if Resume.objects.filter(pract_tasks=search).exists():
                    resumespart = Resume.objects.filter(pract_tasks=search)

                    for image in resumespart:
                        image.birthday, image.grade, image.institution, image.curator, image.spec, image.skills, \
                        image.projects, image.project_links, image.education, image.first_lang, image.other_lang, \
                        image.country, image.pract_name, image.pract_period_from, image.pract_period_to, image.pract_jobs, \
                        image.linkedin, image.pract_tasks = None, None, None, None, None, None, None, None, None, None, None, \
                                                            None, None, None, None, None, None, None
                    done = "1"
                did = 1

        if request.POST.get('users'):
            if Resume.objects.filter(user_id=creator.id).exists():
                resumesfull = Resume.objects.filter(user_id=creator.id)
                chses = "1"
                done = "1"
            did = 1

        if chses == "1" and done == "1":
            for part in resumesfull:
                if part.laptop:
                    part.laptop = "Есть"
                elif part.laptop is False:
                    part.laptop = "Нет"
            resumes = resumesfull

        elif done == "1":
            for part in resumespart:
                if part.laptop:
                    part.laptop = "Есть"
                elif part.laptop is False:
                    part.laptop = "Нет"
            resumes = resumespart

        return render(request, 'show.html', {'resumes': resumes, 'chses': chses, 'srchform': fm, 'tyform': fm2, 'did': did})
    else:
        return redirect('create')


# Представление изменения резюме
@login_required
def updresume(request):
    creator = request.user
    if Resume.objects.filter(user_id=creator.id).exists() or creator.is_staff:
        resumes = None
        did = None
        if request.POST.get('search'):
            search = request.POST.get('search')
            if search.startswith("7"):
                search = "+" + search
            if Resume.objects.filter(phonenum=search).exists():
                resumespart = Resume.objects.filter(phonenum=search)
                for part in resumespart:
                    if part.laptop:
                        part.laptop = "Есть"
                    elif part.laptop is False:
                        part.laptop = "Нет"
                resumes = resumespart
            did = 1
        if request.POST.get('users'):
            if Resume.objects.filter(user_id=creator.id).exists():
                resumespart = Resume.objects.filter(user_id=creator.id)
                for part in resumespart:
                    if part.laptop:
                        part.laptop = "Есть"
                    elif part.laptop is False:
                        part.laptop = "Нет"
                resumes = resumespart
            did = 1
        if request.POST.get('edit'):
            fm = UpdResumeForm(request.POST, request.FILES)
            srch = request.POST.get('resp')
            resumesp = Resume.objects.filter(phonenum=srch)
            did = 1
            resumes = resumesp
            if fm.is_valid():
                resid, usid, num, pho, fi, bi, gra, ins, cur, spe, ski, pro, proli, edu, fir, oth, cou, prana, prafr, \
                prato, prajo, lin, prata, lap = None, None, None, None, None, None, None, None, None, None, None, \
                                                None, None, None, None, None, None, None, None, None, None, None, \
                                                None, None
                for resume in resumesp:
                    resid = resume.id
                    usid = resume.user_id
                    num = resume.phonenum
                    pho, fi, bi, gra, ins, cur, spe, ski, pro, proli, edu, fir, oth, cou, prana, prafr, prato, prajo, \
                    lin, prata, lap = resume.photo, resume.fio, resume.birthday, resume.grade, resume.institution, \
                                      resume.curator, resume.spec, resume.skills, resume.projects, \
                                      resume.project_links, resume.education, resume.first_lang, resume.other_lang, \
                                      resume.country, resume.pract_name, resume.pract_period_from, \
                                      resume.pract_period_to, resume.pract_jobs, resume.linkedin, resume.pract_tasks, \
                                      resume.laptop

                if fm.cleaned_data['photo'] is not None:
                    func.removeImage(str(pho))
                    pho = fm.cleaned_data['photo']
                if len(fm.cleaned_data['fio']) > 0:
                    fi = fm.cleaned_data['fio']
                if fm.cleaned_data['birthday'] is not None:
                    bi = fm.cleaned_data['birthday']
                if len(fm.cleaned_data['grade']) > 0:
                    gra = fm.cleaned_data['grade']
                if len(fm.cleaned_data['institution']) > 0:
                    ins = fm.cleaned_data['institution']
                if len(fm.cleaned_data['curator']) > 0:
                    cur = fm.cleaned_data['curator']
                if len(fm.cleaned_data['spec']) > 0:
                    spe = fm.cleaned_data['spec']
                if len(fm.cleaned_data['skills']) > 0:
                    ski = fm.cleaned_data['skills']
                if len(fm.cleaned_data['projects']) > 0:
                    pro = fm.cleaned_data['projects']
                if len(fm.cleaned_data['project_links']) > 0:
                    proli = fm.cleaned_data['project_links']
                if len(fm.cleaned_data['education']) > 0:
                    edu = fm.cleaned_data['education']
                if len(fm.cleaned_data['first_lang']) > 0:
                    fir = fm.cleaned_data['first_lang']
                if len(fm.cleaned_data['other_lang']) > 0:
                    oth = fm.cleaned_data['other_lang']
                if len(fm.cleaned_data['country']) > 0:
                    cou = fm.cleaned_data['country']
                if len(fm.cleaned_data['pract_name']) > 0:
                    prana = fm.cleaned_data['pract_name']
                if fm.cleaned_data['pract_period_from'] is not None:
                    prafr = fm.cleaned_data['pract_period_from']
                if fm.cleaned_data['pract_period_to'] is not None:
                    prato = fm.cleaned_data['pract_period_to']
                if len(fm.cleaned_data['pract_jobs']) > 0:
                    prajo = fm.cleaned_data['pract_jobs']
                if len(fm.cleaned_data['linkedin']) > 0:
                    lin = fm.cleaned_data['linkedin']
                if len(fm.cleaned_data['pract_tasks']) > 0:
                    prata = fm.cleaned_data['pract_tasks']
                lap = fm.cleaned_data['laptop']

                reg = Resume(id=resid, photo=pho, fio=fi, phonenum=num, birthday=bi, grade=gra, institution=ins,
                             curator=cur,
                             spec=spe, skills=ski, projects=pro, project_links=proli, education=edu, first_lang=fir,
                             other_lang=oth, country=cou, pract_name=prana, pract_period_from=prafr,
                             pract_period_to=prato, pract_jobs=prajo, linkedin=lin, pract_tasks=prata, laptop=lap,
                             user_id=usid)
                reg.save()
                return redirect('homepage')
        else:
            fm = UpdResumeForm()

        return render(request, 'update.html', {'resumes': resumes, 'form': fm, 'did': did})
    else:
        return redirect('create')


# Представление удаления резюме
@login_required
def delresume(request):
    creator = request.user
    if Resume.objects.filter(user_id=creator.id).exists() or creator.is_staff:
        resumes = None
        delamount = None
        did = None
        if request.POST.get('search'):
            search = request.POST.get('search')
            if search.startswith("7"):
                search = "+" + search
            if Resume.objects.filter(phonenum=search).exists():
                resumespart = Resume.objects.filter(phonenum=search)
                resumesp = resumespart
                for part in resumespart:
                    if part.laptop:
                        part.laptop = "Есть"
                    elif part.laptop is False:
                        part.laptop = "Нет"
                resumes = resumespart
            did = 1
        if request.POST.get('users'):
            if Resume.objects.filter(user_id=creator.id).exists():
                resumespart = Resume.objects.filter(user_id=creator.id)
                resumesp = resumespart
                for part in resumespart:
                    if part.laptop:
                        part.laptop = "Есть"
                    elif part.laptop is False:
                        part.laptop = "Нет"
                resumes = resumespart
            did = 1
        if request.POST.get('delete'):
            search = request.POST.get('srchva')
            duser = request.POST.get('deluser')
            target = Resume.objects.filter(phonenum=search)
            if duser != "None" and duser == "on":
                val = [User.objects.all()]
                try:
                    val.append(User.objects.get(id=int(target.values("user_id")[0]["user_id"])))
                except ObjectDoesNotExist or MultipleObjectsReturned:
                    ret = False
                else:
                    result3 = val
                    ret = True
                if ret:
                    if target.values("photo")[0]["photo"] is not None:
                        func.removeImage(str(target.values("photo")[0]["photo"]))
                    if not result3[1].is_staff:
                        result3[0].filter(id=result3[1].id).delete()
                    else:
                        target.delete()
            else:
                if target.values("photo")[0]["photo"] is not None:
                    func.removeImage(str(target.values("photo")[0]["photo"]))
                target.delete()
            return redirect('homepage')
        if request.POST.get('deleteold'):
            result2 = Resume.objects.all()
            today = date.today()
            y = 0
            for i in result2:
                if i.pract_period_to < today:
                    val = [User.objects.all()]
                    try:
                        val.append(User.objects.get(id=i.user_id))
                    except ObjectDoesNotExist or MultipleObjectsReturned:
                        ret = False
                    else:
                        result3 = val
                        ret = True
                    if ret:
                        if i.photo is not None:
                            func.removeImage(str(i.photo))
                        if not result3[1].is_staff:
                            result3[0].filter(id=result3[1].id).delete()
                        else:
                            i.delete()
                        y += 1
            delamount = y
        return render(request, 'delete.html', {'resumes': resumes, 'damount': delamount, 'did': did})
    else:
        return redirect('create')


# Представление регистрации
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            reg = form.save()
            value = "Guests"
            group = Group.objects.get(name=value)
            group.user_set.add(reg)
            reg.save()

            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'signup.html', {'form': form})
