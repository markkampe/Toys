/*
 * synnopsis:
 *	icalc  value	[rate] [term]	future value of lump sum
 *	icalc  payment	[rate] [term]	future value of a serries of investments
 *	icalc -a[/mqys] value [rate] [term]	annuity for a lump sum
 *	icalc -p value	[rate] [term]	present worth of a future lump sum
 *	icalc -p payment [rate] [term]	present worth of a serries of payments
 *
 *		<number>%[mqsy]		interest rate (compounded m/q/y)
 *		<number>m		term in months
 *		<number>y		term in years
 *		<number>/m		monthly payment
 *		<number>/q		quarterly payment
 *		<number>/y		annual payment
 *		<number>		single value
 *		+<number>%		annual growth rate for payments
 *
 *	if no rate is specified, run 6,8,10,12,14
 *	if two rates are specified, run between them by ones
 *
 *	if no term is specified, run 1-10,12-20,25-50
 *	if two terms are specified, run between them by years
 */

#include <stdio.h>
#include <stdlib.h>

/* basic types on which we operate				*/
typedef unsigned long money_t;	/* value in cents (max 40M)	*/
typedef unsigned long rate_t;	/* rate in decipoints/year	*/
typedef unsigned int  month_t;	/* term in months		*/

#ifndef NO_LONG_LONG
typedef unsigned long long calc_t;/* used for calculations	*/
#else
typedef double calc_t;		/* used for calculations	*/
#endif

/* maximum array sizes for table computations			*/
#define MAX_RATES	20	/* maximum number of rates	*/
#define	MAX_TERMS	50	/* maximum number of terms	*/
money_t values[MAX_TERMS][MAX_RATES];	/* table for results	*/

/* if no interest rates are specifed, these are the defaults	*/
#define	DEF_RATES	6	/* default number of rates	*/
rate_t rates[MAX_RATES] = {	/* rates to use for computation	*/
	70,	80,	90,	100,	120,	140
};

/* if no investment term is specifed, these are the defaults	*/
#define	DEF_TERMS	22	/* default number of terms	*/
month_t terms[MAX_TERMS] = {	/* terms to use for computation	*/
	 1*12,	 2*12,	 3*12,	 4*12,	 5*12,	 6*12,	 7*12,	 8*12,
	 9*12,	10*12,	12*12,	14*12,	15*12,	16*12,	18*12,	20*12,	
	25*12,	30*12,	35*12,	40*12,	45*12,	50*12
};


/*
 * routine:
 *	usage:
 *
 * purpose:
 *	print out a usage message
 */
char *umsg[] = {
"usage:	icalc -f value [rate] [term]          ... future worth of lump sum",
"	icalc -f payment/[mqsy] [rate] [term] ... future worth of serries",
"	icalc -p value [rate] [term]          ... present worth of future sum",
"	icalc -p payment/[mqsy] [rate] [term] ... present worth of serries",
"	icalc -[amq] nestegg [rate] [term]    ... annuity from lump sum",
"	      -e ................................ payments at end of year",
" ",
"	rate    #.#%[mqsy]      specify interest rate and compounding period",
"	term    #[my]           specify invesment term in months or years",
"	growth	+#.#%		specify growth rate for payments",
" ",
"       if two rates/terms are specified, the entire range is tabulated",
0
};

void usage()
{	int i;

	for (i = 0; umsg[i]; i++ )
		fprintf(stderr, "%s\n", umsg[i]);

	exit( -1 );
}

/*
 * routine:
 *	fw_lump
 *
 * purpose:
 *	future value of a lump sum today
 *
 * parameters:
 *	lump sum
 *	interest rate, and compounding period
 *	term of investment	(in months)
 *
 * returns:
 *	value at end of term
 */
money_t fw_lump(	money_t value, 
			rate_t rate, month_t compound, 
			month_t term)
{	calc_t earn;
	month_t m;

	/*
	 * At each compounding period, compute and add the earned interest.
	 */
	for (m = 0; m < term; m += compound) {
		earn = value;
		earn *= rate;
		earn /= 1000;	/* rate expressed in decipercent */
			
		/* final accrual period may be shorter than compound period */
		earn *= (term - m > compound) ? compound : term - m;
		earn /= 12;

		value += earn;
	}

	return (value);
}

/*
 * routine:
 *	fw_serries
 *
 * purpose:
 *	future value of a series of investments, earning simple annual interest
 *
 * parameters:
 *	contribution amount , and interval
 *	interest rate, and compounding period
 *	term of investment
 *	growth rate and compounding period
 *
 * returns:
 *	value at end of term
 */
money_t fw_serries(	money_t contrib, month_t interval,
			rate_t rate, month_t compound,
			month_t term, 
			rate_t growth, month_t gcompound)
{	calc_t earn, tmp;
	money_t value = 0, start = 0;
	month_t i, last_m = 0;

	/*
	 * count through the months
	 *	for each compounding period, compute the interest on the avg bal
	 *	for each deposit period, add the contribution
	 *
	 * note: we add deposits second because interest is paid in arrears
	 *       and so the new deposit has not yet earned any interest.
	 */
	for(i = 0; i <= term; i++) {
		/* is this the last month of a compounding period	*/
		if (((i % compound) == 0) || i == term) {
			/* compute interest on average ballance		*/
			earn = start;
			earn += value;
			earn *= rate;
			earn /= 2000;

			/* scale the rate to the compounding period	*/
			earn *= i - last_m;
			earn /= 12;

			value += earn;
			last_m = i;
		}

		/* final term gets owed interest but no contribution	*/
		if (i >= term)
			break;

		/* the amount of the contributions may grow over time	*/
		if (growth != 0 && i != 0 && (i % gcompound) == 0) {
			tmp = contrib;
			tmp *= growth * gcompound;
			tmp /= 12000;
			contrib += tmp;
		}

		/* add the contributions every contribution interval	*/
		if ((i % interval) == 0)
			value += contrib;

		/* if this is the first month of compounding period	*/
		if ((i % compound) == 0)
			start = value;
	}

	return (value);
}

/*
 * routine:
 *	pw_lump
 *
 * purpose:
 *	the present worth of a single sum at some future time
 *
 * parameters:
 *	value
 *	interest rate and compounding period
 *	term of investment
 *
 * returns:
 *	value at end of term
 */
money_t pw_lump(money_t value, 
		rate_t rate, month_t compound, 
		month_t term)
{	money_t future;
	calc_t  result;

	/*
	 * the easiest way to do this is to compute the future worth
	 * of a unit sum at the specified time, and then apply the 
	 * resulting discount ratio to the specified value
	 */
	future = fw_lump(10000, rate, compound, term);

	/* divide the value by the discount rate			*/
	result = value;
	result *= 10000;
	result /= future;;

	return ((money_t) result);
}

/*
 * routine:
 *	pw_serries
 *
 * purpose:
 *	the present worth of series of payments in the future
 *
 * parameters:
 *	amount and interval for contributions
 *	interest rate and compounding period
 *	term over which payments are made
 *	growth rate and compounding period
 *
 * returns:
 *	present worth
 *
 * note:
 *	interest accrues in arrears, whereas contributions
 *	are at the start of the period.
 */
money_t pw_serries(money_t contrib, month_t interval,
		rate_t rate, month_t compound, 
		month_t term, 
		rate_t growth, month_t gcompound)
{	money_t v = 0;
	calc_t tmp;
	month_t m, m_base = 0;
	rate_t discount = 100000, thisdis;

	for (m = 0; m < term; m++) {
		/*
		 * recompute the discount rate each compound interval
		 */
		if (m != 0 && (m % compound) == 0) {
			tmp = discount;
			tmp *= rate * compound;
			tmp /= 12000;

			discount += tmp;
			m_base = m;
		}

		/*
		 * deal with possble growth in the amound of each contribution
		 */
		if (growth != 0 && m != 0 && (m % gcompound) == 0) {
			tmp = contrib;
			tmp *= growth * gcompound;
			tmp /= 12000;
			contrib += tmp;
		}

		/*
		 * discount each contribution
		 */
		if ((m % interval) == 0) {
			/* figure out the current discount rate	*/
			tmp = discount;
			tmp *= rate;
			tmp *= (m - m_base);
			tmp /= 12000;
			thisdis = discount + tmp;

			/* use that rate to discount the payment */
			tmp = contrib;
			tmp *= 100000;
			tmp /= thisdis;

			v += tmp;
		}
	}

	return (v);
}

/*
 * routine:
 *	annuity
 *
 * purpose:
 *	to compute the annuity associated with a specified value, term and return
 *
 * parameters:
 *	initial nest-egg
 *	rate of return and compounding period
 *	period of payout
 *	payout interval
 *
 * returns:
 *	regular payment amount
 */
money_t annuity(money_t initial, rate_t rate, month_t compound,
		month_t term, month_t interval)
{	calc_t value;
	money_t present = 0;

	/* start by figuring out the present worth of a serries of payments */
	present = pw_serries(10000, interval, rate, compound, term, 0, 0);

	/* invert that ratio and multiply it by the nest-egg	*/
	value = initial;
	value *= 10000;
	value /= present;
	
	return ((money_t) value);
}

/*
 * routine:
 *	getperiod
 * 
 * purpose:
 *	to turn a period code into a period
 *
 * parameters:
 *	character for a period
 *
 * returns:
 *	number of months in period
 */
month_t getperiod( char c )
{
	if (c == 0 || c == 'a' || c == 'y')
		return(12);
	if (c == 's')
		return(6);
	if (c == 'q')
		return(3);
	if (c == 'm')
		return(1);

	fprintf(stderr, "Unrecognized period specification (%c)\n", c);
	fprintf(stderr, "Recognized periods are:\n");
	fprintf(stderr, "\ty ...\tper year\n");
	fprintf(stderr, "\ts ...\tper 6 months\n");
	fprintf(stderr, "\tq ...\tper quarter\n");
	fprintf(stderr, "\tm ...\tper month\n");
	exit( -1 );
}

int main(int argc, char **argv)
{	int i;
	char *s, *s1;
	long v, vdot;
	int n_rate, n_term, r, t;
	int debug = 0;
	int gotplus;
	
	/* basic parameters for the calculation to be performed	*/
	int computation = 'f';
	money_t value = 10000;		/* default $100.00	*/
	rate_t rate = 0, rate1 = 0, growth = 0;
	month_t term = 0, term1 = 0, period = 0, compound = 12, gcompound = 12;

	/* gather together all of the options	*/
	for (i = 1; i < argc; i++) { 
		s = argv[i];
		if (*s == '-') switch (s[1]) {
			case 'a':	/* annuity	*/
			case 'q':	/* annuity paid quarterly */
			case 'm':	/* annuity paid monthly */
				computation = 'a';
				period = getperiod(s[1]);
				break;

			case 'p':	/* present worth	*/
				computation = 'p';
				break;

			case 'f':	/* future value		*/
				computation = 'f';
				break;

			case 'D':
				debug++;
				break;

			default:
				usage();
				break;
		} else {

			/*
			 * deal with the non-switch arguments, whose 
			 * meanings are indicated by their suffixes:
			 *
			 *	number[my]	a term in months or years
			 *	number/[mqsy]	a payment
			 *	number%[mqsy]	a compounding interest rate
			 *	number		a value in dollars
			 *	+number%[mqsy]	a growth rate for payments
			 */
			
			/* see if we start with a plus		*/
			gotplus = (*s == '+');
			if (gotplus)
				s++;

			v = strtol(s, &s1, 10);
			if (s1 == 0 || *s1 == 0) {
				value = (money_t) v * 100;
				continue;
			} 

			/* see if there was a decimal point	*/
			if (*s1 == '.') {
				vdot = (s1[1] - '0') * 10;
				s1 += 2;
				if (*s1 >= '0' && *s1 <= '9') {
					vdot += *s1 - '0';
					s1++;
				}
			} else
				vdot = 0;

			/* deal with suffixes			*/
			switch (*s1) {
			    case 'm':	/* term, in months	*/
			    case 'a':	/* term, in years	*/
			    case 'y':	/* term, in years	*/
			    case 'q':	/* term, in quarters	*/
				if (term == 0)
					term = (month_t) v * getperiod(*s1);
				else
					term1 = (month_t) v * getperiod(*s1);
				break;

			    case '/':	/* payment w/ interval	*/
				value = (money_t) v * 100;
				period = getperiod(s1[1]);
				break;
			
			    case '%':	/* rate w/compounding	*/
				if (gotplus)
					growth = (rate_t) (v * 10) + (vdot/10);
				else if (rate == 0)
					rate = (rate_t) (v * 10) + (vdot / 10);
				else
					rate1 = (rate_t) (v * 10) + (vdot / 10);

				if (gotplus)
					gcompound = getperiod(s1[1]);
				else
					compound = getperiod(s1[1]);
				break;

			    default:	/* an amount w/ decimal point */
				value = (money_t) v * 100;
				value += vdot;
				break;
			}
		}
	}

	/* figure out what interest rates we want to consider	*/
	if (rate) {
		if (rate1) {
			i = (rate1 - rate < 10) ? 1 : 10;
			for (n_rate = 0, r = rate; r <= rate1; r += i)
				rates[n_rate++] = r;
		} else {
			rates[0] = rate;
			n_rate = 1;
		}
	} else
		n_rate = DEF_RATES;

	/* figure out what investment/payout terms we want to consider */
	if (term) {
		if (term1) {
			i = ((term % 12) == 0) ? 12 : 1;
			for (n_term = 0, t = term; t <= term1; t += i)
				terms[n_term++] = t;
		} else {
			terms[0] = term;
			n_term = 1;
		}
	} else
		n_term = DEF_TERMS;

	if (debug) {
		printf("computation = %c\n", computation);
		printf("value = %ld, period = %d\n", value, period);
		printf("rate  = %ld, compound = %d, n_rate = %d\n", 
			rate, compound, n_rate);
		if (growth)
			printf("growth = %ld, compound = %d\n",
				growth, gcompound);
		printf("term  = %d, nterm = %d\n", term, n_term);
	}

	/*
	 * computation type f (future worth, at rate and term)
	 *	period = 0 -> lump sum, else series of payments
	 * computation type p (present worth, at rate and term)
	 *	period = 0 -> lump sum, else series of payments
	 * computation type a (annuity, at rate and term)
	 */
	for (t = 0; t < n_term; t++)
		for (r = 0; r < n_rate; r++)
			switch (computation)
	{   case 'f':	/* future worth		*/
		if (period)
			values[t][r] = fw_serries(value, period, rates[r], 
						compound, terms[t], 
						growth, gcompound);
		else
			values[t][r] = fw_lump(value, rates[r], compound, 
							terms[t]);
		break;

	    case 'p':	/* present worth	*/
		if (period)
			values[t][r] = pw_serries(value, period, rates[r], 
						compound, terms[t], 
						growth, gcompound);
		else
			values[t][r] = pw_lump(value, rates[r], compound, 
							terms[t]);
		break;

	    case 'a':	/* annuity corresponding to a lump sum	*/
		values[t][r] = annuity(value, rates[r], compound, terms[t], 
					period);
		break;
	}

	/* print out the results	*/
	if (n_term == 1 && n_rate == 1)
		printf("%ld.%02ld\n", values[0][0]/100, values[0][0]%100);
	else {
		printf( "term   ");
		for( r = 0; r < n_rate; r++ )
			printf( "%8ld.%1ld%% ", rates[r]/10, rates[r]%10 );
		printf( "\n----   " );
		for( r = 0; r < n_rate; r++ )
			printf("      ----- ");
		printf( "\n" );
		

		for (t = 0; t < n_term; t++) {
			if ((terms[t] % 12) == 0)
				printf("%3dy   ", terms[t]/12);
			else
				printf("%3dm   ", terms[t]);

			for (r = 0; r < n_rate; r++)
				printf("%8ld.%02ld ", values[t][r]/100,
							values[t][r]%100);
			printf("\n");
		}
	}

	return (0);
}
