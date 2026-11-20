function multiply(num1, num2) {
	// figure out the values and their widths
	var val1 = Number(num1);
	var val2 = Number(num2);
	var len1 = num1.length;
	var len2 = num2.length;
	var width = len1 + len2 + 1;	// FIX

	// align and pad them for display
	const pad1 = num1.padStart(width);
	const pad2 = num2.padStart(width);
	const line = "-".repeat(width+1);

	var output = " " + pad2 + "\n";
	output += "x" + pad1 + "\n";
	output += line + "\n";

	return output;
}

