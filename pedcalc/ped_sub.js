function subtract(num1, num2) {
	// figure out the values and their widths
	var val1 = Number(num1);
	var val2 = Number(num2);
	var len1 = num1.length;
	var len2 = num2.length;
	var width = (len1 > len2 ? len1 : len2) + 2
	var [ num_1, num_2 ] = decimal_align(num1, num2);

	// ensure that the minuend is the larger number
	if (val2 > val1) {
		var temp = num_1;
		num_1 = num_2;
		num_2 = temp;
	}

	// align and pad them for display
	const pad1 = num_1.padStart(width);
	const pad2 = num_2.padStart(width);
	const line = "-".repeat(width+1);

	var output = " " + pad1 + "\n";
	output += "-" + pad2 + "\n";
	output += line + "\n";

	return output
}
