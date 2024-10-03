default: colsum

clean:
	rm -f colsum

key_lookup: key_lookup.c
	gcc -o $@ $< -lkeyutils

colsum: colsum.c
	gcc -o $@ -Wall -Wextra $<
