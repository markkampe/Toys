function divide(num1, num2) {
	// figure out the values and their widths
	var dividend = Number(num1);
	var dividend_width = num1.length;
	var divisor = Number(num2);
	var divisor_width = num2.length;

	// output layout
	//	         quotient
	//	       ___________
	//	xxx.yy ) abc.def
	//
	var indent = divisor_width + 3;	    		// " ) ".length == 3
	const vincula_width = dividend_width + 4;	// 2 before, 2 after
	var line2 = ' '.repeat(indent - 2) + '_'.repeat(vincula_width) + "\n";
	var line3 = num2 + " ) " + num1 + "\n"

	// FIX: bring-downs
	var computations = "";
	computations += ' '.repeat(indent) + num1[0] + "\n";
	computations += ' '.repeat(indent-1) + "-" + "0" + "      (" + "0"+"*" + num2 + ")\n";
	computations += ' '.repeat(indent-1) + "--" + "\n";
	computations += ' '.repeat(indent) + num1[0] + "\n";

	// FIX: quotient
	quotient = "xxx.yy";
	var line1 = ' '.repeat(indent) + quotient + "\n";

	return line1 + line2 + line3 + computations;
}

