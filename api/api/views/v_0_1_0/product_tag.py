# coding:utf-8
import logging
from api.views.v_0_1_0 import PRODUCT_TAG_COLLECTION
from api.views.v_0_1_0.schema.product_tag import ProductTagSchema
from bson.objectid import ObjectId
import colander
from cornice.service import Service


product_tags = Service(name='products_tags', path='/v0.1.0/productTags', description="products master tag",
                       cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))

logger = logging.getLogger(__name__)


def validate_product_tag(request):
    try:
        schema = ProductTagSchema()
        new_tag = schema.deserialize(request.json_body['productTag'])
        request.validated['tag'] = new_tag
    except colander.Invalid as e:
        errors = e.asdict()
        for error_name, error_value in errors.items():
            if error_value == 'Required':
                request.errors.add('body', error_name, u"标签名不能为空")
            else:
                request.errors.add('body', error_name, u'发生未知错误')
    except Exception as e:
        request.errors.add('body', 'unhandled_error', e.message)

def generate_tag_item(db, _tag):

    _tag['id'] = str(_tag['_id'])
    del _tag['_id']

    return _tag


@product_tags.get()
def get_all_tags(request):
    db = request.db

    tag_list = []

    if request.GET:
        tag_id_list = [ObjectId(tag_id) for _, tag_id in request.GET.items()]
        for _tag in db[PRODUCT_TAG_COLLECTION].find({'_id': {'$in': tag_id_list}}):
            #转变image
            _tag = generate_tag_item(db, _tag)

            #加入列表
            tag_list.append(_tag)
    else:
        for _tag in db[PRODUCT_TAG_COLLECTION].find():
            #转变image
            _tag = generate_tag_item(db, _tag)

            #加入列表
            tag_list.append(_tag)
    return {'productTags': tag_list}



@product_tags.post(content_type="application/json", validators=(validate_product_tag,))
def add_tag(request):
    new_tag = request.validated['tag']
    db = request.db
    result = db['product_tag'].find_and_modify(query={'name': new_tag['name']}, upsert=True,
                                               update={'$setOnInsert': {'name': new_tag['name']}}, new=True)
    result['id'] = str(result['_id'])
    del result['_id']
    return {'productTag': result}