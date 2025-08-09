from flask import request, jsonify
from flask_login import login_required, current_user
from app.models import MyFavorites
from app import db
from app.api import bp

@bp.route('/api/my_favorites', methods=['GET'])
@login_required
def get_my_favorites():
    favorites = MyFavorites.query.filter_by(user_id=current_user.id).all()
    data = [{
        'id': fav.id,
        'car_id': fav.car_id,
        'car_name': fav.car.name
    } for fav in favorites]
    return jsonify(data)

@bp.route('/api/my_favorites/status', methods=['GET'])
@login_required
def favorites_status():
    car_ids = [int(cid) for cid in request.args.getlist('car_ids')]
    # 查詢所有 car_id 的收藏數量
    counts = {cid: 0 for cid in car_ids}
    for row in db.session.query(MyFavorites.car_id, db.func.count(MyFavorites.id)).filter(MyFavorites.car_id.in_(car_ids)).group_by(MyFavorites.car_id):
        counts[row[0]] = row[1]
    # 查詢目前使用者收藏的所有 car_id
    user_favs = set(
        cid for cid, in db.session.query(MyFavorites.car_id).filter_by(user_id=current_user.id).filter(MyFavorites.car_id.in_(car_ids)).all()
    )
    # 組合結果
    result = []
    for cid in car_ids:
        result.append({
            'car_id': cid,
            'count': counts[cid],
            'is_favorite': cid in user_favs
        })
    return jsonify(result)

@bp.route('/api/my_favorites', methods=['POST'])
@login_required
def add_my_favorite():
    car_id = request.json.get('car_id')
    if not car_id:
        return jsonify({'error': 'car_id required'}), 400
    exists = MyFavorites.query.filter_by(car_id=car_id, user_id=current_user.id).first()
    if exists:
        return jsonify({'message': 'Already added'}), 200
    fav = MyFavorites(car_id=car_id, user_id=current_user.id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': 'Added'}), 201

@bp.route('/api/my_favorites/<int:car_id>', methods=['DELETE'])
@login_required
def delete_my_favorite(car_id):
    fav = MyFavorites.query.filter_by(user_id=current_user.id, car_id=car_id).first()
    if not fav:
        return jsonify({'error': 'Not found'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Deleted'})
