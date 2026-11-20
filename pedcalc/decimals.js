/**
 * mulitply a decimal string by ten (no fp errors)
 *
 * @param {string} number - number to multiply
 * @param {int} power - power of ten to multiply by
 * @return {string} desired product
 */
function times_ten(number, power) {
	if (number == "0")	// the trivial case
		return number;

	for ( let i = 0; i < power; i++ ) {
		var dp = number.indexOf('.');
		if (dp <= 0) {	// integers are trivial
			number += 0;
			continue;
		}

		// it depends where the decimal point is
		var len = number.length;
		if (dp == 1 && number[0] == [0])	// 0.xxx
			if (len == 3)					// 0.x -> x
				number = number[2];
			else
				number = number[2] + '.' + number.substring(3,len);
		else if (dp == len - 2)				// xy.z -> xyz
			number = number.substring(0,dp) + number[dp+1];
		else								// x.yz -> xy.z
			number = number.substring(0,dp) + number[dp+1] +
					 '.' + number.substring(dp+2,len)
	}
	return number;
}

/**
 * divide a decimal string by ten (no fp errors)
 *
 * @param {string} number - number to divide
 * @param {int} power - power of ten to divide by
 * @return {string} desired quotient
 */
function divBy_ten(number, power) {
	if (number == "0")	// the trivial case
		return number;

	for (let i = 0; i < power; i++ ) {
		var dp = number.indexOf('.');
		var len = number.length;
		if (dp < 0)
			if (len == 1)		// x -> 0.x
				number = "0." + number;
			else				// xy -> x.y
				number = number.substring(0, len-1) + '.' + number[len-1];
		else if (dp == 1 && number[0] != '0')	// x.yz->0.xyz
			number = "0." + number[0] + number.substring(2,len);
		else if (dp == 1 && number[0] == '0')	// 0.xyz->0.0xyz
			number = "0.0" + number.substring(2,len);
		else									//xy.z -> x.yz
			number = number.substring(0,dp-1) + '.' +
					 number[dp-1] + number.substring(dp+1,len);
	}
	return number;
}

/**
 * how many decimal places in a number
 *
 * @param {string} number - number to test
 * @return {int} places to the right of the decimal point
 */
function decimal_places(number) {
	var dot = number.indexOf(".");
	return dot <= 0 ? 0 : number.length - (dot+1);
}

/**
 * align decimal points on two numbers
 *		 required for addition and subtraction
 *
 * @param {string} num1 - first number
 * @param {string} num2 - second number
 * @return {string, string} updated strings
 */
function decimal_align(num1, num2) {
	var scale1 = decimal_places(num1);
	var scale2 = decimal_places(num2);

	// if they are different, zero-pad the shorter
	if (scale1 > scale2) {
		if (scale2 == 0)
			num2 += '.';
		for( let i = scale2; i < scale1; i++ )
			num2 += '0';
	} else if (scale2 > scale1) {
		if (scale1 == 0)
			num1 += '.';
		for( let i = scale1; i < scale2; i++ )
			num1 += '0';
	}
	return [ num1, num2 ];
}

/**
 * eliminate leading zeroes
 *
 * @param {string} number - number to clean up
 *				likely has leading white space
 * @return {string} cleaned up string
 */
function no_leading_zeroes(number) {
	// check for simply zero or no leading zeroes
	var stripped = number.trimStart();
	if (stripped == '0')	// the single digit zero
		return number;
	if (stripped[0] != '0')	// no leading zeroes
		return number;

	// copy the string, skipping any leading zeroes
	var newstr = "";
	var gotStuff = false;
	var len = number.length;
	for( let i = 0; i < len; i++ ) {	// in white space
		if (number[i] == ' ')
			newstr += ' ';
		else if (gotStuff || number[i] != '0') {	// past leading zeroes
			gotStuff = true;
			newstr += number[i];
		} else if (i < len && number[i+1] == '.') {	// leading 0.
			gotStuff = true;
			newstr += number[i];
		} else							// leading zero
			newstr += ' ';
	}

	return newstr;
}
