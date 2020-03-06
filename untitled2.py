
def check_sym(root):
	if root.left is not None and root.right is not None
		return recur(root.left, root.right)
	else:
		return False

def recur(left, right):
	# If both left and right are None
	if (left is None and right is None):
		return True

	if left.left is not None and right.right is not None:
		return recur(left.left, right.right)
	else:
		return False

	if left.right is not None and right.left is not None:
		return recur(left.right, right.left)
	else:
		return False