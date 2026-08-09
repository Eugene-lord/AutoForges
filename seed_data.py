from models import (Brand, Model, Engine, Compatibility, Transmission,
                    Differential, Suspension, Brake, Cooling, Electronics,
                    ECU, Turbo, Intercooler, Exhaust, Article, Shop, ShopLink, User,
                    ElectricMotor, Battery, Inverter)
from extensions import db
from sqlalchemy import inspect

def seed():
    inspector = inspect(db.engine)
    if not inspector.has_table('brands'):
        print("Таблиц ещё нет, пропускаем seed")
        return

    if Brand.query.first():
        print("Данные уже есть, пропускаем seed")
        return

    # ---------- БРЕНДЫ ----------
    toyota = Brand(name='Toyota', country='Япония', description='Японский автопроизводитель №1')
    bmw = Brand(name='BMW', country='Германия', description='Баварские моторы')
    honda = Brand(name='Honda', country='Япония', description='Надёжность и технологии')
    nissan = Brand(name='Nissan', country='Япония', description='Спортивные легенды и электрокары')
    subaru = Brand(name='Subaru', country='Япония', description='Полный привод и оппозитные моторы')
    tesla = Brand(name='Tesla', country='США', description='Электромобили будущего')

    db.session.add_all([toyota, bmw, honda, nissan, subaru, tesla])
    db.session.flush()

    # ---------- МОДЕЛИ ----------
    supra = Model(brand_id=toyota.id, name='Supra', generation='A80', year_start=1993, year_end=2002,
                  body_type='Купе', description='Легендарная JDM-икона')
    e46 = Model(brand_id=bmw.id, name='3 серия', generation='E46', year_start=1998, year_end=2006,
                body_type='Седан/Купе/Универсал', description='Популярная платформа для свапов')
    civic = Model(brand_id=honda.id, name='Civic', generation='EG/EK', year_start=1991, year_end=2000,
                  body_type='Хэтчбек/Седан', description='Лёгкий кузов для мощных моторов')
    silvia = Model(brand_id=nissan.id, name='Silvia', generation='S15', year_start=1999, year_end=2002,
                   body_type='Купе', description='Дрифт-икона')
    mark2 = Model(brand_id=toyota.id, name='Mark II', generation='JZX100', year_start=1996, year_end=2001,
                  body_type='Седан', description='Комфортный седан с турбо-рядом')
    impreza = Model(brand_id=subaru.id, name='Impreza WRX STI', generation='GD', year_start=2001, year_end=2007,
                    body_type='Седан/Универсал', description='Полноприводная легенда')
    model3 = Model(brand_id=tesla.id, name='Model 3', generation='Standard', year_start=2017, year_end=None,
                   body_type='Седан', description='Электрический седан')
    leaf = Model(brand_id=nissan.id, name='Leaf', generation='ZE1', year_start=2010, year_end=None,
                 body_type='Хэтчбек', description='Массовый электромобиль')
    prius = Model(brand_id=toyota.id, name='Prius', generation='XW50', year_start=2015, year_end=2022,
                  body_type='Лифтбек', description='Гибридный автомобиль')

    db.session.add_all([supra, e46, civic, silvia, mark2, impreza, model3, leaf, prius])
    db.session.flush()

    # ---------- ДВИГАТЕЛИ ----------
    engine_2jz = Engine(engine_code='2JZ-GTE', name='2JZ-GTE', displacement=3.0, power_hp=280, torque_nm=440, fuel_type='Бензин', configuration='I6')
    engine_1jz = Engine(engine_code='1JZ-GTE', name='1JZ-GTE', displacement=2.5, power_hp=280, torque_nm=363, fuel_type='Бензин', configuration='I6')
    engine_m54b30 = Engine(engine_code='M54B30', name='M54B30', displacement=3.0, power_hp=231, torque_nm=300, fuel_type='Бензин', configuration='I6')
    engine_m52b28 = Engine(engine_code='M52B28', name='M52B28', displacement=2.8, power_hp=193, torque_nm=280, fuel_type='Бензин', configuration='I6')
    engine_s54 = Engine(engine_code='S54B32', name='S54B32', displacement=3.2, power_hp=343, torque_nm=365, fuel_type='Бензин', configuration='I6')
    engine_b16a2 = Engine(engine_code='B16A2', name='B16A2', displacement=1.6, power_hp=160, torque_nm=150, fuel_type='Бензин', configuration='L4')
    engine_b18c = Engine(engine_code='B18C', name='B18C', displacement=1.8, power_hp=200, torque_nm=185, fuel_type='Бензин', configuration='L4')
    engine_k20a = Engine(engine_code='K20A', name='K20A', displacement=2.0, power_hp=220, torque_nm=196, fuel_type='Бензин', configuration='L4')
    engine_sr20det = Engine(engine_code='SR20DET', name='SR20DET', displacement=2.0, power_hp=250, torque_nm=280, fuel_type='Бензин', configuration='L4')
    engine_rb25det = Engine(engine_code='RB25DET', name='RB25DET', displacement=2.5, power_hp=250, torque_nm=319, fuel_type='Бензин', configuration='I6')
    engine_rb26dett = Engine(engine_code='RB26DETT', name='RB26DETT', displacement=2.6, power_hp=280, torque_nm=368, fuel_type='Бензин', configuration='I6')
    engine_ej20 = Engine(engine_code='EJ20', name='EJ20', displacement=2.0, power_hp=280, torque_nm=334, fuel_type='Бензин', configuration='H4')
    engine_ej25 = Engine(engine_code='EJ257', name='EJ257', displacement=2.5, power_hp=300, torque_nm=407, fuel_type='Бензин', configuration='H4')
    engine_2jz_swap = Engine(engine_code='2JZ-GTE-SWAP', name='2JZ-GTE (свап)', displacement=3.0, power_hp=280, torque_nm=440, fuel_type='Бензин', configuration='I6')
    engine_2zr_fxe = Engine(engine_code='2ZR-FXE', name='2ZR-FXE', displacement=1.8, power_hp=98, torque_nm=142, fuel_type='Гибрид', configuration='L4')

    db.session.add_all([engine_2jz, engine_1jz, engine_m54b30, engine_m52b28, engine_s54,
                       engine_b16a2, engine_b18c, engine_k20a, engine_sr20det, engine_rb25det, engine_rb26dett,
                       engine_ej20, engine_ej25, engine_2jz_swap, engine_2zr_fxe])
    db.session.flush()

    engine_2jz.model_id = supra.id
    engine_1jz.model_id = mark2.id
    engine_m54b30.model_id = e46.id
    engine_b16a2.model_id = civic.id
    engine_sr20det.model_id = silvia.id
    engine_ej20.model_id = impreza.id
    engine_2zr_fxe.model_id = prius.id
    db.session.flush()

    # ---------- ТРАНСМИССИИ ----------
    trans_v160 = Transmission(name='Getrag V160', type='МКПП', gears=6)
    trans_r154 = Transmission(name='Toyota R154', type='МКПП', gears=5)
    trans_a340e = Transmission(name='A340E', type='АКПП', gears=4)
    trans_zf5hp19 = Transmission(name='ZF 5HP19', type='АКПП', gears=5)
    trans_getrag250 = Transmission(name='Getrag 250G', type='МКПП', gears=5)
    trans_s15_6mt = Transmission(name='S15 6MT', type='МКПП', gears=6)
    trans_subaru5mt = Transmission(name='Subaru 5MT', type='МКПП', gears=5)
    trans_subaru6mt = Transmission(name='Subaru 6MT', type='МКПП', gears=6)
    trans_ecvt = Transmission(name='eCVT', type='Вариатор', gears=None)

    db.session.add_all([trans_v160, trans_r154, trans_a340e, trans_zf5hp19, trans_getrag250,
                       trans_s15_6mt, trans_subaru5mt, trans_subaru6mt, trans_ecvt])
    db.session.flush()

    # ---------- РЕДУКТОРЫ ----------
    diff_torsen = Differential(name='Torsen LSD', type='LSD', ratio=3.266)
    diff_open = Differential(name='Открытый дифференциал', type='Открытый', ratio=3.727)
    diff_kaaz = Differential(name='Kaaz 1.5-way LSD', type='LSD', ratio=4.1)
    diff_subaru_r160 = Differential(name='Subaru R160 LSD', type='LSD', ratio=4.11)
    diff_nissan_r200 = Differential(name='Nissan R200', type='LSD', ratio=4.083)

    db.session.add_all([diff_torsen, diff_open, diff_kaaz, diff_subaru_r160, diff_nissan_r200])
    db.session.flush()

    # ---------- ПОДВЕСКИ ----------
    susp_stock = Suspension(name='Стоковая подвеска', type='Пружины/амортизаторы')
    susp_tein = Suspension(name='Tein Flex Z', type='Койловеры')
    susp_air = Suspension(name='AirREX', type='Пневмоподвеска')
    susp_bilstein = Suspension(name='Bilstein B12', type='Спортивные амортизаторы')
    susp_ohlins = Suspension(name='Ohlins Road & Track', type='Койловеры')

    db.session.add_all([susp_stock, susp_tein, susp_air, susp_bilstein, susp_ohlins])
    db.session.flush()

    # ---------- ТОРМОЗА ----------
    brake_stock = Brake(name='Стоковые тормоза', type='Дисковые', size='296 мм')
    brake_brembo = Brake(name='Brembo GT', type='Дисковые', size='355 мм')
    brake_wilwood = Brake(name='Wilwood', type='Дисковые', size='330 мм')
    brake_sti_4pot = Brake(name='Subaru 4-pot', type='Дисковые', size='326 мм')

    db.session.add_all([brake_stock, brake_brembo, brake_wilwood, brake_sti_4pot])
    db.session.flush()

    # ---------- ОХЛАЖДЕНИЕ ----------
    cool_stock = Cooling(name='Стоковый радиатор', type='Медный')
    cool_alum = Cooling(name='Koyo Aluminium', type='Алюминиевый')
    cool_oil = Cooling(name='Маслокулер Setrab', type='Дополнительный')
    cool_mishimoto = Cooling(name='Mishimoto X-Line', type='Алюминиевый')

    db.session.add_all([cool_stock, cool_alum, cool_oil, cool_mishimoto])
    db.session.flush()

    # ---------- ЭЛЕКТРОНИКА ----------
    elec_stock = Electronics(name='Стоковая проводка', description='Подходит для стоковых двигателей')
    elec_custom = Electronics(name='Кастомная проводка', description='Для свапов, универсальная')

    db.session.add_all([elec_stock, elec_custom])
    db.session.flush()

    # ---------- ЭБУ ----------
    ecu_stock = ECU(name='Стоковый ЭБУ', type='OEM')
    ecu_haltech = ECU(name='Haltech Elite 2500', type='Standalone')
    ecu_link = ECU(name='Link G4+', type='Standalone')
    ecu_aem = ECU(name='AEM Infinity', type='Standalone')

    db.session.add_all([ecu_stock, ecu_haltech, ecu_link, ecu_aem])
    db.session.flush()

    # ---------- ТУРБИНЫ ----------
    turbo_stock = Turbo(name='CT12B (сток)', pressure='0.7 бар')
    turbo_gt35 = Turbo(name='Garrett GT35', pressure='1.5 бар')
    turbo_pt6766 = Turbo(name='Precision PT6766', pressure='2.0 бар')
    turbo_td05 = Turbo(name='Mitsubishi TD05', pressure='1.2 бар')
    turbo_gtx3071 = Turbo(name='Garrett GTX3071R', pressure='1.8 бар')

    db.session.add_all([turbo_stock, turbo_gt35, turbo_pt6766, turbo_td05, turbo_gtx3071])
    db.session.flush()

    # ---------- ИНТЕРКУЛЕРЫ ----------
    inter_stock = Intercooler(name='Стоковый интеркулер', type='Боковой')
    inter_hks = Intercooler(name='HKS Type-R', type='Фронтальный')
    inter_greddy = Intercooler(name='Greddy 4-рядный', type='Фронтальный')
    inter_perrin = Intercooler(name='Perrin Front Mount', type='Фронтальный')

    db.session.add_all([inter_stock, inter_hks, inter_greddy, inter_perrin])
    db.session.flush()

    # ---------- ВЫХЛОП ----------
    exhaust_stock = Exhaust(name='Стоковый выхлоп', material='Сталь')
    exhaust_hks = Exhaust(name='HKS Hi-Power', material='Нержавейка')
    exhaust_tomei = Exhaust(name='Tomei Expreme Ti', material='Титан')
    exhaust_invidia = Exhaust(name='Invidia N1', material='Нержавейка')

    db.session.add_all([exhaust_stock, exhaust_hks, exhaust_tomei, exhaust_invidia])
    db.session.flush()

    # ---------- ЭЛЕКТРОКОМПОНЕНТЫ ----------
    motor_tesla = ElectricMotor(name='Tesla M3 Rear Motor', power_hp=283, torque_nm=420, motor_type='Синхронный')
    motor_leaf = ElectricMotor(name='Nissan Leaf EM57', power_hp=147, torque_nm=320, motor_type='Синхронный')
    motor_prius = ElectricMotor(name='Toyota Prius MG2', power_hp=71, torque_nm=163, motor_type='Синхронный')

    battery_tesla = Battery(name='Tesla Model 3 LR Battery', capacity_kwh=75, voltage=350, battery_type='Li-Ion')
    battery_leaf = Battery(name='Nissan Leaf 40 kWh', capacity_kwh=40, voltage=360, battery_type='Li-Ion')
    battery_prius = Battery(name='Toyota Prius NiMH', capacity_kwh=1.3, voltage=201, battery_type='NiMH')

    inverter_tesla = Inverter(name='Tesla Model 3 Inverter', power_kw=211, inverter_type='SiC MOSFET')
    inverter_leaf = Inverter(name='Nissan Leaf Inverter', power_kw=110, inverter_type='IGBT')
    inverter_prius = Inverter(name='Toyota Prius Inverter', power_kw=60, inverter_type='IGBT')

    db.session.add_all([motor_tesla, motor_leaf, motor_prius, battery_tesla, battery_leaf, battery_prius,
                       inverter_tesla, inverter_leaf, inverter_prius])
    db.session.flush()

    # ---------- ФУНКЦИЯ ДОБАВЛЕНИЯ СОВМЕСТИМОСТЕЙ ----------
    def add_comp(model, comp_type, component, status, desc, cost=0, diff=1):
        db.session.add(Compatibility(
            vehicle_model_id=model.id,
            component_type=comp_type,
            component_id=component.id,
            status=status,
            description=desc,
            estimated_cost=cost,
            difficulty=diff
        ))

    # ---------- СОВМЕСТИМОСТИ (ВСЕ МОДЕЛИ) ----------
    # Supra
    add_comp(supra, 'engine', engine_2jz, 'compatible', 'Родной двигатель')
    add_comp(supra, 'engine', engine_1jz, 'warning', 'Требуется замена подушек, проводки и ЭБУ', 1500, 4)
    add_comp(supra, 'engine', engine_rb26dett, 'incompatible', 'Требуется серьёзная переработка', 5000, 9)
    add_comp(supra, 'transmission', trans_v160, 'compatible', 'Стоковая 6-ст МКПП')
    add_comp(supra, 'transmission', trans_r154, 'compatible', 'Альтернативная 5-ст', 800, 2)
    add_comp(supra, 'differential', diff_torsen, 'compatible', 'Стоковый LSD')
    add_comp(supra, 'differential', diff_kaaz, 'compatible', 'Усиленный LSD', 1200, 3)
    add_comp(supra, 'suspension', susp_stock, 'compatible', 'Родная')
    add_comp(supra, 'suspension', susp_tein, 'compatible', 'Tein Flex Z', 900, 2)
    add_comp(supra, 'brakes', brake_stock, 'compatible', 'Сток')
    add_comp(supra, 'brakes', brake_brembo, 'compatible', 'Brembo GT', 2500, 3)
    add_comp(supra, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(supra, 'cooling', cool_alum, 'compatible', 'Koyo Aluminium', 400, 2)
    add_comp(supra, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(supra, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(supra, 'ecu', ecu_haltech, 'compatible', 'Haltech Elite', 1500, 4)
    add_comp(supra, 'turbo', turbo_stock, 'compatible', 'Сток CT12B')
    add_comp(supra, 'turbo', turbo_gt35, 'warning', 'Garrett GT35, кастомный коллектор', 2500, 6)
    add_comp(supra, 'intercooler', inter_stock, 'compatible', 'Сток')
    add_comp(supra, 'intercooler', inter_hks, 'compatible', 'HKS Type-R', 900, 3)
    add_comp(supra, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(supra, 'exhaust', exhaust_hks, 'compatible', 'HKS Hi-Power', 800, 2)

    # E46
    add_comp(e46, 'engine', engine_m54b30, 'compatible', 'Родной двигатель')
    add_comp(e46, 'engine', engine_m52b28, 'compatible', 'Менее мощный')
    add_comp(e46, 'engine', engine_s54, 'warning', 'M3 мотор, доработки трансмиссии', 3000, 6)
    add_comp(e46, 'transmission', trans_getrag250, 'compatible', 'Стоковая МКПП')
    add_comp(e46, 'transmission', trans_zf5hp19, 'compatible', 'Стоковая АКПП')
    add_comp(e46, 'differential', diff_open, 'compatible', 'Открытый')
    add_comp(e46, 'differential', diff_torsen, 'warning', 'LSD от M3', 900, 4)
    add_comp(e46, 'suspension', susp_stock, 'compatible', 'Родная')
    add_comp(e46, 'suspension', susp_bilstein, 'compatible', 'Bilstein B12', 700, 2)
    add_comp(e46, 'brakes', brake_stock, 'compatible', 'Сток')
    add_comp(e46, 'brakes', brake_brembo, 'warning', 'Brembo GT, нужны адаптеры', 2600, 4)
    add_comp(e46, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(e46, 'cooling', cool_mishimoto, 'compatible', 'Mishimoto X-Line', 350, 2)
    add_comp(e46, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(e46, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(e46, 'turbo', turbo_stock, 'compatible', 'Атмосферный')
    add_comp(e46, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(e46, 'exhaust', exhaust_invidia, 'compatible', 'Invidia N1', 700, 2)

    # Civic
    add_comp(civic, 'engine', engine_b16a2, 'compatible', 'Родной двигатель')
    add_comp(civic, 'engine', engine_b18c, 'compatible', 'Свап B18C', 1200, 2)
    add_comp(civic, 'engine', engine_k20a, 'warning', 'K20A, нужны переходные плиты', 3000, 6)
    add_comp(civic, 'differential', diff_open, 'compatible', 'Открытый')
    add_comp(civic, 'differential', diff_kaaz, 'compatible', 'Kaaz LSD', 1100, 4)
    add_comp(civic, 'suspension', susp_stock, 'compatible', 'Родная')
    add_comp(civic, 'suspension', susp_tein, 'compatible', 'Tein Flex Z', 850, 3)
    add_comp(civic, 'brakes', brake_stock, 'compatible', 'Сток')
    add_comp(civic, 'brakes', brake_wilwood, 'compatible', 'Wilwood', 1400, 4)
    add_comp(civic, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(civic, 'cooling', cool_alum, 'compatible', 'Koyo', 380, 2)
    add_comp(civic, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(civic, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(civic, 'turbo', turbo_stock, 'compatible', 'Атмо')
    add_comp(civic, 'turbo', turbo_td05, 'warning', 'Турбо-кит TD05', 2200, 6)
    add_comp(civic, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(civic, 'exhaust', exhaust_hks, 'compatible', 'HKS', 650, 2)

    # Silvia S15
    add_comp(silvia, 'engine', engine_sr20det, 'compatible', 'Родной двигатель')
    add_comp(silvia, 'engine', engine_rb25det, 'warning', 'RB25DET, замена креплений', 2500, 7)
    add_comp(silvia, 'transmission', trans_s15_6mt, 'compatible', 'Стоковая 6-ст')
    add_comp(silvia, 'differential', diff_nissan_r200, 'compatible', 'Nissan R200')
    add_comp(silvia, 'differential', diff_kaaz, 'compatible', 'Kaaz 1.5-way', 1000, 3)
    add_comp(silvia, 'suspension', susp_stock, 'compatible', 'Сток')
    add_comp(silvia, 'suspension', susp_ohlins, 'compatible', 'Ohlins R&T', 1800, 3)
    add_comp(silvia, 'brakes', brake_stock, 'compatible', 'Сток')
    add_comp(silvia, 'brakes', brake_brembo, 'warning', 'Brembo, адаптеры', 2300, 4)
    add_comp(silvia, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(silvia, 'cooling', cool_alum, 'compatible', 'Koyo', 400, 2)
    add_comp(silvia, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(silvia, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(silvia, 'turbo', turbo_stock, 'compatible', 'Сток T28')
    add_comp(silvia, 'turbo', turbo_gtx3071, 'warning', 'GTX3071R, кастомный даунпайп', 2800, 7)
    add_comp(silvia, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(silvia, 'exhaust', exhaust_tomei, 'compatible', 'Tomei Expreme Ti', 1100, 2)

    # Mark II JZX100
    add_comp(mark2, 'engine', engine_1jz, 'compatible', 'Родной двигатель')
    add_comp(mark2, 'engine', engine_2jz_swap, 'warning', 'Свап 2JZ-GTE', 2000, 5)
    add_comp(mark2, 'transmission', trans_r154, 'compatible', 'Стоковая 5-ст МКПП')
    add_comp(mark2, 'transmission', trans_a340e, 'compatible', 'Стоковая АКПП')
    add_comp(mark2, 'differential', diff_torsen, 'compatible', 'Torsen LSD')
    add_comp(mark2, 'differential', diff_kaaz, 'compatible', 'Kaaz LSD', 1100, 3)
    add_comp(mark2, 'suspension', susp_stock, 'compatible', 'Сток')
    add_comp(mark2, 'suspension', susp_tein, 'compatible', 'Tein Flex Z', 880, 2)
    add_comp(mark2, 'brakes', brake_stock, 'compatible', 'Сток')
    add_comp(mark2, 'brakes', brake_brembo, 'warning', 'Brembo GT, адаптеры', 2400, 4)
    add_comp(mark2, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(mark2, 'cooling', cool_mishimoto, 'compatible', 'Mishimoto', 360, 2)
    add_comp(mark2, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(mark2, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(mark2, 'turbo', turbo_stock, 'compatible', 'Сток CT15B')
    add_comp(mark2, 'turbo', turbo_gt35, 'warning', 'Garrett GT35', 2600, 6)
    add_comp(mark2, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(mark2, 'exhaust', exhaust_hks, 'compatible', 'HKS Hi-Power', 780, 2)

    # Impreza WRX STI
    add_comp(impreza, 'engine', engine_ej20, 'compatible', 'Родной двигатель')
    add_comp(impreza, 'engine', engine_ej25, 'compatible', 'EJ257, bolt-on', 800, 2)
    add_comp(impreza, 'transmission', trans_subaru5mt, 'compatible', 'Стоковая 5-ст')
    add_comp(impreza, 'transmission', trans_subaru6mt, 'compatible', '6-ст STI', 1200, 2)
    add_comp(impreza, 'differential', diff_subaru_r160, 'compatible', 'R160 LSD')
    add_comp(impreza, 'differential', diff_kaaz, 'warning', 'Kaaz LSD, доработка', 1400, 5)
    add_comp(impreza, 'suspension', susp_stock, 'compatible', 'Сток')
    add_comp(impreza, 'suspension', susp_ohlins, 'compatible', 'Ohlins R&T', 2100, 3)
    add_comp(impreza, 'brakes', brake_sti_4pot, 'compatible', 'Subaru 4-pot')
    add_comp(impreza, 'brakes', brake_brembo, 'compatible', 'Brembo STI', 500, 2)
    add_comp(impreza, 'cooling', cool_stock, 'compatible', 'Сток')
    add_comp(impreza, 'cooling', cool_mishimoto, 'compatible', 'Mishimoto X-Line', 380, 2)
    add_comp(impreza, 'electronics', elec_stock, 'compatible', 'Сток')
    add_comp(impreza, 'ecu', ecu_stock, 'compatible', 'Сток')
    add_comp(impreza, 'turbo', turbo_td05, 'compatible', 'Сток TD05')
    add_comp(impreza, 'turbo', turbo_gtx3071, 'warning', 'GTX3071R, кастомный фланец', 3000, 7)
    add_comp(impreza, 'exhaust', exhaust_stock, 'compatible', 'Сток')
    add_comp(impreza, 'exhaust', exhaust_invidia, 'compatible', 'Invidia N1', 720, 2)

    # Tesla Model 3
    add_comp(model3, 'electric_motor', motor_tesla, 'compatible', 'Родной электромотор')
    add_comp(model3, 'battery', battery_tesla, 'compatible', 'Родная батарея')
    add_comp(model3, 'inverter', inverter_tesla, 'compatible', 'Родной инвертор')
    add_comp(model3, 'transmission', trans_ecvt, 'compatible', 'Одноступенчатый редуктор')
    add_comp(model3, 'suspension', susp_stock, 'compatible', 'Сток')
    add_comp(model3, 'brakes', brake_brembo, 'compatible', 'Brembo', 2000, 2)

    # Nissan Leaf
    add_comp(leaf, 'electric_motor', motor_leaf, 'compatible', 'Родной электромотор')
    add_comp(leaf, 'battery', battery_leaf, 'compatible', 'Родная батарея')
    add_comp(leaf, 'inverter', inverter_leaf, 'compatible', 'Родной инвертор')
    add_comp(leaf, 'transmission', trans_ecvt, 'compatible', 'Редуктор')
    add_comp(leaf, 'suspension', susp_tein, 'compatible', 'Tein Flex Z', 900, 3)
    add_comp(leaf, 'brakes', brake_stock, 'compatible', 'Сток')

    # Toyota Prius
    add_comp(prius, 'engine', engine_2zr_fxe, 'compatible', 'Гибридный ДВС')
    add_comp(prius, 'electric_motor', motor_prius, 'compatible', 'Родной электромотор')
    add_comp(prius, 'battery', battery_prius, 'compatible', 'NiMH батарея')
    add_comp(prius, 'inverter', inverter_prius, 'compatible', 'Родной инвертор')
    add_comp(prius, 'transmission', trans_ecvt, 'compatible', 'Планетарный вариатор')
    add_comp(prius, 'suspension', susp_bilstein, 'compatible', 'Bilstein B12', 700, 2)
    add_comp(prius, 'brakes', brake_wilwood, 'warning', 'Wilwood, адаптеры', 1400, 4)

    # ---------- СТАТЬИ ----------
    articles = [
        Article(title='Свап 2JZ-GTE в BMW E46', category='swap',
                content='Подробное руководство...', tags='2JZ,E46'),
        Article(title='Выбор КПП для Supra', category='transmission',
                content='Обзор...', tags='Supra,КПП'),
        Article(title='Турбины для 2JZ', category='turbo',
                content='Сравнение...', tags='2JZ,турбина'),
        Article(title='Замена батареи Tesla Model 3', category='electric',
                content='Рекомендации...', tags='Tesla,батарея'),
        Article(title='Электрификация Nissan Leaf', category='electric',
                content='Апгрейд батареи...', tags='Leaf,батарея'),
    ]
    db.session.add_all(articles)

    # ---------- МАГАЗИНЫ ----------
    shop_exist = Shop(name='Exist.ru', affiliate_code='AUTOFORGE')
    shop_emex = Shop(name='Emex', affiliate_code='AUTOFORGE')
    shop_ebay = Shop(name='eBay Motors', affiliate_code='AUTOFORGE')
    db.session.add_all([shop_exist, shop_emex, shop_ebay])
    db.session.flush()

    comp_2jz = Compatibility.query.filter_by(vehicle_model_id=supra.id, component_type='engine', component_id=engine_2jz.id).first()
    comp_v160 = Compatibility.query.filter_by(vehicle_model_id=supra.id, component_type='transmission', component_id=trans_v160.id).first()
    if comp_2jz:
        db.session.add_all([
            ShopLink(compatibility_id=comp_2jz.id, shop_id=shop_exist.id, price=3500, url='https://exist.ru/2jz'),
            ShopLink(compatibility_id=comp_2jz.id, shop_id=shop_emex.id, price=3200, url='https://emex.ru/2jz'),
        ])
    if comp_v160:
        db.session.add(ShopLink(compatibility_id=comp_v160.id, shop_id=shop_ebay.id, price=4200, url='https://ebay.com/v160', currency='USD'))

    # ---------- АДМИН ----------
    if not User.query.first():
        admin = User(username='admin', email='admin@AUTOFORGE.com', is_admin=True)
        admin.set_password('admin')
        db.session.add(admin)
        print("Создан администратор: admin / admin")

    db.session.commit()
    print("Seed выполнен успешно (все 9 моделей)")
