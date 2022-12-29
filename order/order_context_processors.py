from .models import ShopCart


def shopcart(request):
    if request.user.is_authenticated:
        current_user = request.user
        shopcart = ShopCart.objects.filter(user_id=current_user.id)
        total = 0
        items = 0
        for rs in shopcart:
            total += rs.variant.price * rs.quantity
            items += rs.quantity
        return {'total': total,'items':items}
    return{}