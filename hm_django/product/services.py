#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Created by flytrap
from .models import Product, Brand


class ProductService(object):
    @classmethod
    def get_like_category(cls, user):
        # 考虑加缓存
        ps = Product.objects.filter(likeproduct__user=user, likeproduct__is_valid=True).select_related('brand')
        brands = ps.order_by('brand_id').distinct().values('brand_id', 'brand__name', 'brand__icon')
        results = []
        from .serializers import ListProductSerializer
        for brand in brands:
            data = {"products": ListProductSerializer(ps.filter(brand_id=brand['brand_id'])[:3], many=True).data}
            data.update(
                {'brand_id': brand['brand_id'], 'brand_name': brand['brand__name'], 'brand_icon': brand['brand__icon']})
            results.append(data)

        return results

    @classmethod
    def get_brand(cls, brand_id: int):
        brands = getattr(cls, '_brands', {})
        if brand_id in brands:
            return brands[brand_id]
        brands[brand_id] = Brand.objects.filter(id=brand_id).first()
        setattr(cls, '_brands', brands)
        return brands[brand_id]

    @classmethod
    def get_like_brand_ids(cls, user):
        return Brand.objects.filter(likebrand__user=user, likebrand__is_valid=True).values_list('id', flat=True)
