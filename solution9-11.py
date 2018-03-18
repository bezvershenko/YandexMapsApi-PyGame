# coding:utf-8
import sys
import os
import math

import pygame
import requests

from gui import GUI, ButtonFlag, TextBox, DivButtons, Div, ButtonImage, Button, TextBlock, Switch
from geocoder import get_coordinates, get_address, get_postal_code

pygame.init()

satellite = {'normal': 'image/buttons/satellite.png', 'hovered': 'image/buttons/satellite_hovered.png',
             'clicked': 'image/buttons/satellite_active.png'}
scheme = {'normal': 'image/buttons/scheme.png', 'hovered': 'image/buttons/scheme_hovered.png',
          'clicked': 'image/buttons/scheme_active.png'}
gibrid = {'normal': 'image/buttons/gibrid.png', 'hovered': 'image/buttons/gibrid_hovered.png',
          'clicked': 'image/buttons/gibrid_active.png'}
buts = {'normal': 'image/buttons/but.png', 'hovered': 'image/buttons/but_hovered.png',
        'clicked': 'image/buttons/but_active.png'}


def update_static(ll, z, map_type, add_params=None):
    if ll:
        map_request = "http://static-maps.yandex.ru/1.x/?ll={ll}&z={z}&l={map_type}".format(**locals())
    else:
        map_request = "http://static-maps.yandex.ru/1.x/?l={map_type}".format(**locals())

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)

    if not response:
        return None

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    try:
        with open(map_file, "wb") as file:
            file.write(response.content)
            return map_file
    except IOError as ex:
        print("Ошибка записи временного файла:", ex)
        sys.exit(2)


def change_view(_view):
    global map_type, flag_update_map
    map_type = _view
    flag_update_map = True


def get_coord(lon, lat, text_box_name=None, address=None, text_block=None, switch=None):
    _address = address

    if text_box_name:
        text_box = GUI.get_object(text_box_name)
        if text_box.text != text_box.default_text:
            _address = text_box.text

    if _address != None:
        post_code(switch, _address)
        coords = get_coordinates(_address)

        if coords != (None, None):
            globals()[lon], globals()[lat] = coords
            globals()['flag_update_map'] = True
            globals()['_pt'] = 'pt={},{},pm2rdm'.format(coords[0], coords[1])

            if text_block:
                _address_ = get_address(_address).split(', ')
                text_block.text = [_address_[0], ', '.join(_address_[1:])]
                if globals()['postcode']:
                    text_block.text.append(globals()['postcode'])


def post_code(_status_switch, _address):
    if _status_switch and _address:
        globals()['postcode'] = get_postal_code(_address)
    if not _status_switch and _address:
        globals()['postcode'] = ''


def clear_search(search, tb):
    search.text = ''
    tb.text = []
    globals()['_pt'] = None
    globals()['flag_update_map'] = True


def show_map(ll, z, _map_type='map', add_params=None):
    global map_type, flag_update_map
    global _lat, _lon, _pt, address, postcode

    flag_update_map = False
    postcode = None
    address = None
    map_type = _map_type

    pygame.init()
    screen = pygame.display.set_mode((600, 540))
    _z = z
    _lat, _lon = map(float, ll.split(','))
    _pt = add_params
    _tb_info = TextBlock((2, 452, 490, 86), [],
                         24, text_color=(77, 81, 83), bg_color=(255, 255, 255), name='tb_info')
    GUI.add_element(_tb_info)

    buttons_view = DivButtons(ButtonFlag((546, 465), buts, func=lambda: change_view('map'), text='Схема',
                                         text_size=23, name='but_satellite', shift_text=(-4, 0)),
                              ButtonFlag((546, 495), buts, func=lambda: change_view('sat'), text='Спутник',
                                         text_size=23, name='but_scheme', shift_text=(4, 0)),
                              ButtonFlag((546, 525), buts, func=lambda: change_view('sat,skl'), text='Гибрид',
                                         text_size=23, name='but_gibrid', shift_text=(3, 0)))
    buttons_view.elements[0].states['clicked'] = True
    GUI.add_element(buttons_view)
    search = TextBox((40, 5, 400, 30), '', default_text='Введите адрес...', name='tb_address')
    search_div = Div(search,
                     Button('X', (425, 21), (29, 28), lambda: clear_search(search, _tb_info),
                            'delete', but_color=(255, 255, 255), hovered=(190, 190, 190), size_font=24,
                            shift_text=(10, 7)),
                     Button('Поиск', (500, 21), (100, 30),
                            lambda: get_coord('_lat', '_lon', 'tb_address', text_block=_tb_info, switch=switch.on),
                            'but_search', but_color=(255, 255, 255), hovered=(190, 190, 190), size_font=24,
                            shift_text=(21, 7)))

    GUI.add_element(search_div)
    switch = Switch((411, 512, 40, 25), 'Индекс', color_switch=(62, 151, 209), color_background=(240, 248, 255),
                    color_background_on=(240, 248, 255), func=lambda: post_code(switch.on, globals()[
            'address']))  # func = lambda: get_post_code() globals()['address']
    GUI.add_element(switch)

    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

    clock = pygame.time.Clock()

    while True:
        screen.fill((254, 202, 131))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os.remove(map_file)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_PAGEUP or event.key == pygame.K_w:
                    if _z - 1 >= 2:
                        _z -= 1
                        map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

                elif event.key == pygame.K_PAGEDOWN or event.key == pygame.K_s:
                    if _z + 1 <= 17:
                        _z += 1
                        map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

                elif event.key == pygame.K_RIGHT:
                    _lat += 422.4 / (2 ** (_z - 1))
                    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

                elif event.key == pygame.K_LEFT:
                    _lat -= 422.4 / (2 ** (_z - 1))
                    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

                elif event.key == pygame.K_UP:
                    _lon += 178.25792 / (2 ** (_z - 1))
                    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

                elif event.key == pygame.K_DOWN:
                    _lon -= 178.25792 / (2 ** (_z - 1))
                    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if 30 < pos[1] < 450:
                    x_k = (422.4 / (2 ** (_z - 1))) / 600
                    y_k = (178.25792 / (2 ** (_z - 1))) / 450

                    x, y = pos[0] - 300, 225 - pos[1]
                    lat, lon = _lat + x * x_k, _lon + y * y_k
                    clear_search(search, _tb_info)
                    post_code(switch.on, ','.join([str(lat), str(lon)]))
                    _pt = 'pt={},{},pm2rdm'.format(lat, lon)
                    _address_ = get_address(','.join([str(lat), str(lon)])).split(', ')
                    _tb_info.text = [_address_[0], ', '.join(_address_[1:])]
                    map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)
                    if globals()['postcode']:
                        _tb_info.text.append(globals()['postcode'])

            GUI.apply_event(event)

        clock.tick(60)

        if flag_update_map:
            map_file = update_static(','.join([str(_lat), str(_lon)]), _z, map_type, _pt)
            flag_update_map = False

        screen.blit(pygame.image.load(map_file), (0, 0))

        GUI.update()
        GUI.render(screen)
        pygame.display.flip()


def main():
    ll = "45.983259,51.536890"
    z = 16
    show_map(ll, z, "map")


if __name__ == "__main__":
    main()
