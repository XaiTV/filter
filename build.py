import argparse
import os

def get_var_from_line(line):
    split_line = line.strip().split(' ')
    if split_line[0].startswith('$'):
        return split_line[0]
    else:
        return None

def main(args):
    with open(args.var_base_file, 'r') as fp:
        var_lines = fp.readlines()
    
    if args.var_file:
        new_lines = []
        with open(args.var_file, 'r') as fp:
            for line in fp.readlines() + var_lines:
                var = get_var_from_line(line)
                # if the var isn't used before, the line can be added
                if not any(get_var_from_line(line2) == var for line2 in new_lines):
                    new_lines.append(line)

        var_lines = new_lines

    with open(args.filter, 'r') as fp:
        filter_lines = fp.readlines()

    # let's be nice and add a newline between the var and filter
    combined_lines = var_lines + [''] + filter_lines

    with open(args.temp_file, 'w') as fp:
        fp.writelines(combined_lines)

    # @TODO: don't use os.system, it's lame and potentially unsafe
    os.system('{0} -g --input-path {1} --output-path={2} -e'.format(
        args.spirit, args.temp_file, args.output,
    ))
    print('Filter now available at: {0}'.format(args.output))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter Spirit variable helper')
    parser.add_argument('--var-base-file', '-b', default='base.vars', help='The variable file you want to use as a base')
    parser.add_argument('--var-file', '-v', required=False, help='The variable file you want to use to override base vars')
    parser.add_argument('--filter', '-f', default='xai.filter_spirit', help='The filter file you want to use')
    parser.add_argument('--spirit', '-s', required=True, help='The path to the filter spirit executable')
    parser.add_argument('--output', '-o', default='xai.filter', help='The path you want to output the final filter to')
    parser.add_argument('--temp-file', '-t', default='_filter.tmp', help='Path to temporary file to store combined filter in')

    main(parser.parse_args())
