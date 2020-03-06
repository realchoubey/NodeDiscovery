'''
1 -> 2 -> 5 -> 8

3 -> 4 -> 6
'''

def merge_sorted_list(list1, list2):
	main_head = None
	if list1.val < list2.val:
		main_head = list1
		temp_min = list1
		temp_max = list2
	else:
		main_head = list2
		temp_min = list2
		temp_max = list1


	while (temp_min.next is not None) and (temp_max is not None):
		if temp_min.next.val > temp_max.val:
			# Merge
			temp_curr = temp_min.next

			temp_min.next = temp_max

			temp_max = temp_max.next

			temp_min = temp_min.next
			temp_min.next = temp_curr
		else:
			temp_min = temp_min.next

	# Max list is remeaning just add it to temp_min
	if temp_max is not None:
		temp_min.next = temp_max

	return main_head