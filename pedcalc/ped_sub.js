/**
 * pedagogical subtraction, showing borrows
 *
 * @param {string} num1 - minuend 
 * @param {string} num2 - subtrahend
 *		note, both are positive, smaller will be subtracted from larger
 *
 * @reutrn {string} decimal alligned results:
 *			     borrows
 *			     /  / //
 *			     minuend
 *		    + subtrahend
 *			 -----------
 *			  difference
 */
function subtract(num1, num2) {
	// get them to the same decimal precision
	var [ num_1, num_2 ] = decimal_align(num1, num2);

	// ensure that the minuend is the larger number
	var val1 = Number(num1);
	var val2 = Number(num2);
	if (val2 > val1) {
		var temp = num_1;
		num_1 = num_2;
		num_2 = temp;
		temp = val1;
		val1 = val2;
		val2 = temp;
	}

	// pad both numbers to the same number of characters
	var len1 = num_1.length;
	var len2 = num_2.length;
	var width = (len1 > len2 ? len1 : len2) + 1;
	var pad1 = num_1.padStart(width);
	var pad2 = num_2.padStart(width);
	var line = "-".repeat(width+1);

	// make copies of the digits for subtraction and borrowing
	digits1 = new Array(width).fill(0);
	digits2 = new Array(width).fill(0);
	for( let i = 0; i < width; i++ ) {
		if (pad1[i] != ' ' && pad1[i] != '.')
				digits1[i] = Number(pad1[i]);
		if (pad2[i] != ' ' && pad2[i] != '.')
				digits2[i] = Number(pad2[i]);
	}

	// do the subtraction
	var result = "";		// (characters) accumulated difference
	var borrows = false;	// we have not yet done any borrows
	for( let i = width - 1; i >= 0; i-- ) {
		// skip over decimal points (same place in all strings/arrays)
		if (pad1[i] == '.') {
			result = '.' + result;
			continue;
		}

		// do we have to borrow for this digit
		if (digits1[i] < digits2[i]) {
			// find previous non-zero digit to borrow from
			var borrow_x = i - 1;
			while (borrow_x > 0 && digits1[borrow_x] == 0)
				borrow_x -= 1;
			// borrow from that digit
			digits1[borrow_x] -= 1;
			// pass it down to the digit that needs it
			for( let j = borrow_x+1; j < i; j++ ) {
				digits1[j] = 9;
			}

			digits1[i] += 10;
			borrows = true;
		}
		result = String(digits1[i] - digits2[i]) + result;
	}

	// validate our results with (binary) subtraction
	var ok = "\n";
	var sb = val1 - val2;
	if (Number(result) != sb) {
		// error may be due to binary floating point
		const places = decimal_places(result);
		if (places > 0)
			sb = sb.toFixed(places);
		if (Number(result) != sb)
			ok = "    (should be " + String(sb) + ")\n";
	}

	// capture and print the borrows
	var output = "";
	if (borrows) {
		borrow_10s = "";
		borrow_01s = "";
		for( let i = 0; i < width; i++ ) {
			original = pad1[i];
			if (original == ' ' || original == '.') {
				borrow_10s += ' ';
				borrow_01s += ' ';
				continue;
			}
			if (Number(original) == digits1[i]) {
				borrow_10s += ' ';
				borrow_01s += ' ';
				continue;
			}
			borrow_10s += (digits1[i] >= 10) ? '1' : ' ';
			borrow_01s += String(digits1[i] % 10)
		}
		output += "(" + borrow_10s + "    10s borrows)\n";
		output += "(" + borrow_01s + "     1s borrows)\n";
	}
	// generate the regular output
	output += " " + pad1 + "\n";
	output += "-" + pad2 + "\n";
	output += line + "\n";
	output += " " + no_leading_zeroes(result) + ok;

	return output
}
