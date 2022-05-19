from app import app, db
from app.models import Auto, Arenda, Image
from flask import render_template, request, redirect, url_for
from datetime import datetime
from app.forms import AutoDetailForm, CreateAutoForm, AddImageForm, UpdateAutoForm
from shutil import rmtree
import os


# Функция проверки требуемого расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Главная страница с выводом всех автомобилей
@app.route('/index')
@app.route('/')
def index():
    
    # Получаем все записи из таблицы Auto
    auto_list = Auto.query.all()

    context = {
        'auto_list': auto_list
    }

    return render_template('index.html', **context)

# Страница детальной информации авто
@app.route('/auto_detail/<int:auto_id>', methods=['POST', 'GET'])
def auto_detail(auto_id):

    #Получаем выгрузку данных по id авто
    auto = Auto.query.get(auto_id)
    #Проверка ввода данных пользователем
    form = AutoDetailForm()
    form.validate_on_submit()

    # Вывод АККП
    if auto.transmission:
        get_transmission = "Автомат"
    else:
        get_transmission = "Механика"

       # Вывод аренды данного авто
    rent_list = Arenda.query.filter_by(auto_id=auto.id)
    #  Добавленние данных вбазу по нажатию кнопки "Арендовать"/"завершить аренду"
    if form.validate_on_submit():
        total_time = 0
        if auto.in_rent_or_free:
            date_rent = auto.date
            time_rent = (datetime.now().replace(microsecond=0) - auto.date).seconds
            cost_of_rent = round((time_rent/60)*auto.price, 2)
            auto.date = datetime.now().replace(microsecond=0)
            auto.in_rent_or_free = False
            # Добавляем Arenda в базу данных
            db.session.add(Arenda(auto_id=auto.id, date_free=datetime.now().replace(microsecond=0), date_rent=date_rent,
                                  in_rent_or_free=auto.in_rent_or_free, time_rent=time_rent, cost_of_rent=cost_of_rent))

            auto.count_rent = db.session.query(Arenda).filter_by(auto_id= auto.id).count()

        else:
            auto.date = datetime.now().replace(microsecond=0)
            auto.in_rent_or_free = True

        for time in rent_list:
            total_time += time.time_rent
        auto.all_time_rent = round(total_time / 60, 2)
        auto.total_cost_of_rent = round(auto.price * total_time / 60, 2)
        db.session.commit()

        # Вывод Доступности
    if auto.in_rent_or_free:
        get_in_rent_or_free = "Занят"
    else:
        get_in_rent_or_free = "Свободен"

    context = {
        'id': auto.id,
        'name': auto.name,
        'auto_description': auto.description,
        'transmission': get_transmission,
        'price': auto.price,
        'img_list': auto.image,
        'get_in_rent_or_free': get_in_rent_or_free,
        'in_rent': auto.in_rent_or_free
        }

    return render_template('auto_detail.html', **context, form=form)


#Страница создания авто
@app.route('/auto_create', methods=['POST', 'GET'])
def auto_create():

    form = CreateAutoForm()
    err = False
    if form.validate_on_submit():
        
        # Пришел запрос с методом POST (пользователь нажал на кнопку 'Добавить auto')
        # Получаем название auto - это значение поля input с атрибутом name="name"
        auto_name = form.name.data

        # Получаем описание auto - это значение поля input с атрибутом name="description"
        auto_description = form.description.data

        # Получаем цену auto - это значение поля input с атрибутом name="price"
        auto_price = form.price.data

        # Получаем АКПП auto - это значение поля input с атрибутом name="transmission"
        auto_transmission = form.transmission.data

        # Получаем картинку auto
        file = form.main_image.data
        #Проверяем расширение картинки, если правда
        if allowed_file(file.filename):

            # Добавляем auto в базу данных
            db.session.add(
                Auto(name=auto_name, description=auto_description, price=auto_price, transmission=auto_transmission))

            # сохраняем изменения в базе
            db.session.commit()

            # Получаем id новой строки
            auto = Auto.query.order_by(Auto.id).filter_by(name=auto_name).first()
            # Создаем папку для картинок с названием id новой машины
            os.chdir(os.path.join(app.config['STATIC_ROOT'], 'assets/images/auto/'))
            try:
                os.mkdir(str(auto.id))
            except Exception as e:
                print('Папку не создать, причина:', e)
            finally:
                main_image = f'assets/images/auto/{auto.id}/{file.filename}'
            #Сохраняем картинку в созданную или существующую папку
            file.save(os.path.join(app.config['STATIC_ROOT'], main_image))

            # Добавляем image в базу данных
            db.session.add(
                Image(auto_id=auto.id, img_url=main_image))

            # сохраняем изменения в базе
            db.session.commit()

            return redirect('/index')
        else:
            err = f'Файл не является картинкой'

    return render_template('auto_create.html', form=form, err=err)


#Страница обновления информации об авто
@app.route('/auto_update/<int:auto_id>', methods=['POST', 'GET'])
def auto_update(auto_id):
    auto = Auto.query.get(auto_id)
    rent_list = Arenda.query.filter_by(auto_id=auto.id).all()
    img_list = Image.query.filter_by(auto_id=auto.id).all()
    form = UpdateAutoForm(name=auto.name, description=auto.description, price=auto.price,
                           main_image=auto.image)

    if form.validate_on_submit():

        action = request.form.get('action', '')
        if action == 'save':
            # Пришел запрос с методом POST (пользователь нажал на кнопку 'Изменить')
            # Получаем новое название auto - это значение поля input с атрибутом name="name"
            auto.name = form.name.data

            # Получаем новое описание auto - это значение поля input с атрибутом name="description"
            auto.description = form.description.data

            # Получаем новую цену auto - это значение поля input с атрибутом name="price"
            auto.price = form.price.data

            # Получаем новое АКПП auto - это значение поля input с атрибутом name="transmission"
            auto_transmission = form.transmission.data
            auto.transmission = auto_transmission

            # Получаем новые картинку auto
            file = form.main_image.data

            # Проверяем расширение картинки, если правда
            if allowed_file(file.filename):
                try:
                    old_image = os.path.join(app.config['STATIC_ROOT'], img_list[0].img_url)
                except:
                    return redirect(f'/auto_images/{auto.id}')

                main_image = f'assets/images/auto/{auto.id}/{file.filename}'
                # Заменяем путь image в базе данных
                image = Image.query.get(img_list[0].id)
                image.img_url = main_image
                # Сохраняем картинку в созданную или существующую папку
                file.save(os.path.join(app.config['STATIC_ROOT'], main_image))
                # Удаляем файл картинки из папки авто
                if os.path.isfile(old_image):
                    os.remove(old_image)

            # сохраняем изменения в базе
            db.session.commit()

    return render_template('auto_update.html', form=form, rent_list=rent_list, img_list=img_list, id=auto.id)


@app.route('/auto_images/<int:auto_id>', methods=['POST', 'GET'])
def auto_images(auto_id):
    auto = Auto.query.get(auto_id)

    err = False

    image_list = Image.query.filter_by(auto_id=auto.id).all()
    url_list = []
    for img in image_list:
        url_list.append(img.img_url)
    success_url = url_for('auto_images', auto_id=auto.id)

    form = AddImageForm(main_image=auto.image)
    form.validate_on_submit()

    if form.validate_on_submit():
        action = request.form.get('action', '')
        if action == 'add':
            # Получаем картинку auto
            file = form.main_image.data
            # Проверяем расширение картинки, если правда
            if allowed_file(file.filename):
                main_image = f'assets/images/auto/{auto.id}/{file.filename}'
                #Проверяем есть ли файл с тем же названием
                if main_image not in url_list:
                    # Сохраняем картинку в существующую папку auto.id
                    file.save(os.path.join(app.config['STATIC_ROOT'], main_image))

                    # Добавляем image в базу данных
                    db.session.add(
                        Image(auto_id=auto.id, img_url=main_image))

                    # сохраняем изменения в базе
                    db.session.commit()
                    return redirect(success_url)
                else:
                    err = f'Уже есть такой файл.'

            else:
                err = f'Файл не является картинкой'

        elif action == 'del':

            db.session.delete(image_list[0])
            # сохраняем изменения в базе
            db.session.commit()
            return redirect(success_url)

    context = {
        'id': auto.id,
        'name': auto.name,
        'img_list': image_list
    }

    db.session.commit()

    return render_template('auto_images.html', **context, form=form, err=err)


@app.route('/rental_log')
def rental_log():
    auto_list = Auto.query.all()
        
    context = {
        'auto_list': auto_list,
    }
    return render_template('rental_log.html', **context)


@app.route('/del_auto/<int:auto_id>', methods=['POST'])
def del_auto(auto_id):
    auto = Auto.query.get(auto_id)
    # rent_list = Arenda.query.filter_by(auto_id = auto.id)
    context = {
        'id': auto.id,
        'name': auto.name
    }
    # for rent in rent_list:
    # db.session.delete(rent)

    db.session.delete(auto)
    db.session.commit()

    return render_template('del_auto.html', **context)

# функция удаления картинки авто на странце редактирования картинок auto_images
@app.route('/del_image/<int:auto_id>/<int:img_id>', methods=['GET', 'POST'])
def del_image(auto_id, img_id):
    #Получаем информацию о требуемой картинке
    auto = Auto.query.get(auto_id)
    del_image = Image.query.get(img_id)
    path_image = os.path.join(app.config['STATIC_ROOT'], del_image.img_url)

    #Удаляем строку картинки из базы данных
    db.session.delete(del_image)
    # сохраняем изменения в базе
    db.session.commit()

    #Удаляем файл картинки из папки авто
    if os.path.isfile(path_image):
        os.remove(path_image)

    # Страница возврата
    return redirect(url_for('auto_images', auto_id=auto.id))

