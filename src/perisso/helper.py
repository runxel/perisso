# `zip()` stops at the shortest list,
# `itertool` needs either a "fillvalue" to be set, or it cycles.
# Instead we want to repeat the last item in the smaller lists:
def zip_repeat_last(*lists):
	max_len = max(map(len, lists))
	for i in range(max_len):
		yield tuple(lst[i] if i < len(lst) else lst[-1] for lst in lists)


def _printcol(text: str):
	text = "\033[91m" + text + "\033[0m"
	print(text)
