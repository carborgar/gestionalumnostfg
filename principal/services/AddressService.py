# -*- coding: utf-8 -*-
__author__ = 'Carlos'

from principal.models import Direccion


def reconstruct_and_save(address_formset, student):
    if student.ficha:
        residence_address = student.ficha.direccion_residencia
        address_studying = student.ficha.direccion_estudios

        # Update residence address
        residence_address.direccion = address_formset[0].cleaned_data['address']
        residence_address.localizacion = address_formset[0].cleaned_data['location']
        residence_address.pais = address_formset[0].cleaned_data['country']
        residence_address.provincia = address_formset[0].cleaned_data['province']
        residence_address.codigo_postal = address_formset[0].cleaned_data['postal_code']

        # Update address while studying
        address_studying.direccion = address_formset[1].cleaned_data['address']
        address_studying.localizacion = address_formset[1].cleaned_data['location']
        address_studying.pais = address_formset[1].cleaned_data['country']
        address_studying.provincia = address_formset[1].cleaned_data['province']
        address_studying.codigo_postal = address_formset[1].cleaned_data['postal_code']

    else:
        residence_address = Direccion(
            direccion=address_formset[0].cleaned_data['address'],
            localizacion=address_formset[0].cleaned_data['location'],
            pais=address_formset[0].cleaned_data['country'],
            provincia=address_formset[0].cleaned_data['province'],
            codigo_postal=address_formset[0].cleaned_data['postal_code'],
        )

        address_studying = Direccion(
            direccion=address_formset[1].cleaned_data['address'],
            localizacion=address_formset[1].cleaned_data['location'],
            pais=address_formset[1].cleaned_data['country'],
            provincia=address_formset[1].cleaned_data['province'],
            codigo_postal=address_formset[1].cleaned_data['postal_code'],
        )

    residence_address.save()
    address_studying.save()

    return [residence_address, address_studying]
