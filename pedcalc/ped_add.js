function add(num1, num2) {
	// figure out the values, length and number of decimal places
	var val1 = Number(num1);
	var len1 = num1.length;
	var val2 = Number(num2);
	var len2 = num2.length;

	// align and pad them for display
	var width = (len1 > len2 ? len1 : len2) + 2
	const [ num_1, num_2 ] = decimal_align(num1, num2);
	var pad1 = num_1.padStart(width);
	var pad2 = num_2.padStart(width);
	var line = "-".repeat(width+1);

	var output = " " + pad1 + "\n";
	output += "+" + pad2 + "\n";
	output += line + "\n";

	return output
}
