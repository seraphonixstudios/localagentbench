def discounted(subtotal):
    if subtotal > 100:
        return subtotal - (subtotal * 0.1)
    return subtotal

# Existing code for total_standard() and total_member() should call discounted(subtotal) instead of duplicate logic

def total_standard(subtotal):
    return discounted(subtotal) + taxes()  # Assuming taxes() is existing logic

def total_member(subtotal):
    return discounted(subtotal) * 0.95  # Assuming 5% member discount is existing logic