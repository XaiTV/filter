import argparse

def main(args):
    with open(args.var_file, 'r') as fp:
        var_lines = fp.readlines()

    with open(args.filter, 'r') as fp:
        filter_lines = fp.readlines()

    # let's be nice and add a newline between the var and filter
    combined_lines = var_lines + [''] + filter_lines

    with open(args.temp_file, 'w') as fp:
        fp.writelines(combined_lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter Spirit variable helper')
    parser.add_argument('--var-file', '-v', required=True, help='The variable file you want to use')
    parser.add_argument('--filter', '-f', required=True, help='The filter file you want to use')
    parser.add_argument('--spirit', '-s', required=True, help='The path to the filter spirit executable')
    parser.add_argument('--temp-file', '-t', required=False, default='_filter.tmp', help='Path to temporary file to store combined filter in')

    main(parser.parse_args())
