from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.contrib.auth.views import logout
from django.contrib.auth import authenticate, login
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from django.utils.translation import ugettext
from .models import Comment, Parking, Selected, UserData


#Función que loguea al usuario si ya existe ese usuario y coinicide con la
#contraseña, si no coincide no logue y si el usuario no existe lo crea.
def myLogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            #Si existe y coincide loguea
            login(request, user)
            return HttpResponseRedirect(username)
        else:
            try:
                #Si existe y no coincide no loguea
                user = User.objects.get(username=username)
                return HttpResponseRedirect("/")
            except:
                #Si no existe crea el usuario y lo loguea
                user_model = User.objects.create_user(username=username, password=password)
                user_model.save()
                user = authenticate(username=username, password=password)
                login(request, user)
                title = ugettext("Page of: ") + username
                elemento = UserData(name=username, background="white", size=1, title=title)
                elemento.save()
                return HttpResponseRedirect(username)


def myLogout(request):
    logout(request)
    return HttpResponseRedirect('/')


#Función que accede al documento XML de la comunidad de Madrid y
#añade la información de cada uno de los parkings a mi base de datos,
#excepto si falla en atributos importantes como el nombre, el barrio...
@csrf_exempt
def parseador(request):
    if Parking.objects.all().count() == 0:
        tree = ET.parse(urlopen('http://datos.munimadrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=202584-0-aparcamientos-residentes&mgmtid=e84276ac109d3410VgnVCM2000000c205a0aRCRD&preview=full'))
        root = tree.getroot()
        for contenido in root.findall('contenido'):
            atributos = contenido.find('atributos')
            try:
                idNumber = atributos[0].text
                name = atributos[1].text
                description = atributos[2].text

                if atributos[3].text == "1":
                    accessibility = True
                else:
                    accessibility = False

                url = atributos[4].text
                neighborhood = atributos[5][7].text
                district = atributos[5][8].text
                try:
                    latitude = atributos[5][11].text
                    longitude = atributos[5][12].text
                except:
                    latitude = 0
                    longitude = 0
                try:
                    phoneNumber = atributos[6][0].text
                    mail = atributos[6][1].text
                except:
                    phoneNumber = "No Data"
                    mail = "No Data"
                parking = Parking(idNumber=idNumber, name=name, description=description, accessibility=accessibility, url=url, neighborhood=neighborhood, district=district, latitude=latitude, longitude=longitude, phoneNumber=phoneNumber, mail=mail, numberOfComments=0, punctuation=0)
                parking.save()
            except:
                print("Error Creating parcking")
    return HttpResponseRedirect('/')


#Función que sirve la lista de parkings con comentarios y de usuarios
@csrf_exempt
def barra(request):
    if request.method == "GET":
        #Muestro los 5 parkings con mayor número de comentarios
        parkings = Parking.objects.all().filter(numberOfComments__gte=1)\
            .order_by("-numberOfComments")[0:5]
    elif request.method == "POST":
        #Muestro los 5 parkings accesibles con mayor número de comentarios
        parkings = Parking.objects.all().filter(accessibility=True).filter(numberOfComments__gte=1)\
            .order_by("-numberOfComments")[0:5]
    #Listo los usuarios
    users = UserData.objects.all()
    #Carga las templates, mostrando una u otra dependiendo de si el usuario
    #está registrado
    if request.user.is_authenticated():
        user = request.user.username
        arguments = {'parkings': parkings, 'usuarios': users, 'usuario': user}
        return render_to_response('main.html', arguments, context_instance=RequestContext(request))
    arguments = {'parkings': parkings, 'usuarios': users}
    return render_to_response('main.html', arguments, context_instance=RequestContext(request))

#Función que sirve la lista de todos los parkings, además de un botón de
#puntuación y un botón que ofrece la posibilidad de seleccionar un
#aparcamiento si estás logueado
@csrf_exempt
def parkings(request):
    if request.method == 'GET':
        parkings = Parking.objects.all()
    elif request.method == 'POST':
        # Pueden llegar varios tipos de formulario, filtro de distritos,
        # de puntuación o de selección, por tanto es necesario comporbar
        # el campo
        if 'district' in request.POST:
            district = request.POST.get('district', '')
            parkings = Parking.objects.all().filter(district=district)
        elif 'idKey' in request.POST:
            idKey = request.POST.get('idKey', '')
            parking = Parking.objects.get(idNumber=idKey)
            parking.punctuation += 1
            parking.save()
            parkings = Parking.objects.all()
        else:
            info = request.POST.get('key', '')
            state, idKey = info.split("///")
            if state == "Selected":
                parking = Parking.objects.get(idNumber=idKey)
                selected = Selected.objects.get(parking=parking, userName=request.user.username)
                selected.delete()
                parkings = Parking.objects.all()
            else:
                parking = Parking.objects.get(idNumber=idKey)
                selected = Selected(parking=parking, userName=request.user.username)
                selected.save()
                parkings = Parking.objects.all()
    AllParkingsList = ''
    for parking in parkings:
        AllParkingsList += '<li>' + parking.name
        AllParkingsList += '<br>' + ugettext("Information websites: ") + '<a href=aparcamientos/'
        AllParkingsList += str(parking.id)+'>local</a> & '
        AllParkingsList += '<a href='
        AllParkingsList += parking.url+'> Madrid</a>.<br><br>'
        if request.user.is_authenticated():
            #Comprueba si el aparcamiento ha sido ya seleccionado o no para
            # mostrar un boton u otro
            found = False
            parkingsSelected = Selected.objects.all().filter(userName=request.user.username)
            for parkingSelected in parkingsSelected:
                parking2 = parkingSelected.parking
                if parking2.idNumber == parking.idNumber:
                    found = True
            if found:
                AllParkingsList += '<form action="/aparcamientos" method="post" align="right" >'
                AllParkingsList += '<button class=" w3-black inner"  name='"key"' value=Selected///' + parking.idNumber + '>' + ugettext("Selected") + '</button>'
                AllParkingsList += "</form>"
            else:
                AllParkingsList += '<form action="/aparcamientos" method="post" align="right" >'
                AllParkingsList += '<button class=" w3-black inner"  name='"key"' value=NonSelected///' + parking.idNumber + '>' + ugettext("Not Selected") + '</button>'
                AllParkingsList += "</form>"
        AllParkingsList += '<form action="/aparcamientos" method="post" align="right" >'
        AllParkingsList += '<button class=" w3-black inner"  name='"idKey"' value=' + parking.idNumber + '>+1</button>'
        AllParkingsList += "</form>"
    if request.user.is_authenticated():
        user = request.user.username
        arguments = {'contenido': AllParkingsList, 'usuario': user}
        return render_to_response('parkings.html', arguments, context_instance=RequestContext(request))
    else:
        arguments = {'contenido': AllParkingsList}
        return render_to_response('parkings.html', arguments, context_instance=RequestContext(request))

#Función que sirve la información de un parking individual y todos sus
#comentarios, ofreciendo la posibilidad de comentarlo si estás autenticado
def individualParking(request, digit):
    try:
        parking = Parking.objects.get(id=digit)
    except:
        individual = "Parking no encontrado"
        arguments = {'contenido': individual}
        return render_to_response('individual.html', arguments, context_instance=RequestContext(request))
    if request.method == "POST" and request.user.is_authenticated():
        contentComment = request.POST.get('comment', '')
        comment = Comment(parking=parking, content=contentComment)
        comment.save()
        parking.numberOfComments += 1
        parking.save()
    comments = Comment.objects.all().filter(parking=parking)
    if request.user.is_authenticated():
        user = request.user.username
        arguments = {'parking': parking, 'comments': comments, 'usuario': user}
        return render_to_response('individual.html', arguments, context_instance=RequestContext(request))
    arguments = {'parking': parking, 'comments': comments}
    return render_to_response('individual.html', arguments, context_instance=RequestContext(request))


def user(request, username):
    try:
        name, offset = username.split("offset=")
        if offset == "1":
            initialIndex = 0
        else:
            initialIndex = (int(offset) - 1) * 5
        finalIndex = int(offset) * 5
    except:
        path = request.path + "offset=1"
        return HttpResponseRedirect(path)
    try:
        user = User.objects.get(username=name)
    except User.DoesNotExist:
        info = "Lo siento, este usuario no existe"
        arguments = {'contenido': info, 'userPath': name}
        return render_to_response('user.html', arguments, context_instance=RequestContext(request))

    parkingsSelected = Selected.objects.all().filter(userName=user).order_by("date")[initialIndex:finalIndex]
    info = "<h2>Página perteneciente a: " + name + "</h2>"
    if (int(offset) * 5) < Selected.objects.all().filter(userName=user).count():
        path = name + "offset=" + str(int(offset) + 1)
        info += '<strong><a href=' + path + '>Next</a></strong>'

    if request.user.is_authenticated():
        user = request.user.username
        arguments = {'contenido': info, 'parkings': parkingsSelected, 'usuario': user, 'userPath': name}
        return render_to_response('user.html', arguments, context_instance=RequestContext(request))
    else:
        arguments = {'contenido': info, 'parkings': parkingsSelected, 'userPath': name}
        return render_to_response('user.html', arguments, context_instance=RequestContext(request))


# Función que devuelve información sobre la página
def about(request):
    if request.user.is_authenticated():
        user = request.user.username
        arguments = {'usuario': user}
        return render_to_response('about.html', arguments, context_instance=RequestContext(request))
    else:
        arguments = {}
        return render_to_response('about.html', arguments, context_instance=RequestContext(request))


# Función que manda la información de la página de usuario en formato XML
@csrf_exempt
def userxml(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        info = "Lo siento, este usuario no existe"
        return HttpResponse("Este usuario no existe")
    parkingsSelected = Selected.objects.all().filter(userName=user)
    arguments = {'parkingsSelected': parkingsSelected}
    return render_to_response('userxml.xml', arguments, context_instance=RequestContext(request))


# Función que manda la información de la página principal en formato XML
@csrf_exempt
def barraxml(request):
    parkings = Parking.objects.all().filter(numberOfComments__gte=1)\
        .order_by("-numberOfComments")[0:5]
    arguments = {'parkings': parkings}
    return render_to_response('barraxml.xml', arguments, context_instance=RequestContext(request))


# Función que manda la información de la página de usuario en formato JSON
@csrf_exempt
def userjson(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        info = "Lo siento, este usuario no existe"
        return HttpResponse("Este usuario no existe")
    parkingsSelected = Selected.objects.all().filter(userName=user)
    arguments = {'parkingsSelected': parkingsSelected}
    return render_to_response('userjson.json', arguments, context_instance=RequestContext(request))


# Función que manda la información de la página principal en formato JSON
@csrf_exempt
def barrajson(request):
    parkings = Parking.objects.all().filter(numberOfComments__gte=1)\
        .order_by("-numberOfComments")[0:5]
    arguments = {'parkings': parkings}
    return render_to_response('barrajson.json', arguments, context_instance=RequestContext(request))

# Función que manda un canal RSS
def canalRSS(request):
    comments = Comment.objects.all()
    context = {'comments': comments}
    return render_to_response('rss.xml', context, context_instance = RequestContext(request), content_type='application/xml')


# Función que sirve css con distintos datos para cada usuario
def linkcss(request):
    if request.user.is_authenticated():
        username = request.user.username
        try:
            user = UserData.objects.get(name=username)
            if user.background == "":
                arguments = {'fondo': "white", 'textsize': "1em"}
            else:
                arguments = {'fondo': user.background, 'textsize': user.size}
                print(user.size)
            template = get_template("prueba.css")
            return HttpResponse(template.render(arguments), content_type="text/css")
        except:
            arguments = {'fondo': "white", 'textsize': "1em"}
            template = get_template("prueba.css")
            return HttpResponse(template.render(arguments), content_type="text/css")
    arguments = {'fondo': "white", 'textsize': "1em"}
    template = get_template("prueba.css")
    return HttpResponse(template.render(arguments), content_type="text/css")


# Función que cambia o crea si no existe información asociada a un usuario
def changeUserData(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            username = request.user.username
            background = request.POST['background']
            size = request.POST['size']
            title = request.POST['title']
            userOption = UserData.objects.get(name=username)
            if background == "":
                background = userOption.background
            if size == "":
                size = userOption.size
            if title == "":
                title = userOption.title
            try:
                userOption.background = background
                userOption.size = size
                userOption.title = title
                userOption.save()
            except UserData.DoesNotExist:
                elemento = UserData(name=username, background=background, size=size, title=title)
                elemento.save()
    return HttpResponseRedirect('/')

'''
Documentación oficial consultada
    https://docs.djangoproject.com/en/1.11/topics/auth/default/
    https://docs.python.org/2/library/xml.etree.elementtree.html
    https://docs.djangoproject.com/en/1.11/ref/models/querysets/
Templates
    https://www.w3schools.com/w3css/w3css_templates.asp
Inclusión de mapa de google maps
    https://www.w3schools.com/html/html_googlemaps.asp
    https://developers.google.com/maps/web/?hl=es-419
Internacionalización de la página
    https://www.pythoniza.me/multiples-idiomas-en-django/
Javascript de la página pricipal
    https://www.w3schools.com/w3css/tryit.asp?filename=tryw3css_templates_travel2&stacked=h
'''
