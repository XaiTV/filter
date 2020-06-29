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

    toggles = {}
    if args.toggle:
        with open(args.toggle, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if line.startswith('$'):
                    toggle_name, toggle_value = line.split('=')
                    toggle_name = toggle_name.strip()[1:]
                    toggle_value = toggle_value.strip()
                    toggles[toggle_name] = toggle_value
                    
        

    with open(args.filter, 'r') as fp:
        filter_lines = []
        for line in fp.readlines():
            if '#TOGGLE-' in line:
                # PREPARE FOR SOME UGLY ASS CODE
                pre_toggle, after_toggle = line.split('#TOGGLE-')
                toggle_name = after_toggle.strip()
                if toggle_name in toggles:
                    if toggles[toggle_name] == 'Show':
                        pre_toggle = pre_toggle.replace('Hide', 'Show')
                    else:
                        pre_toggle = pre_toggle.replace('Show', 'Hide')
                    
                    line = '#TOGGLE-'.join(pre_toggle, after_toggle)
                
                filter_lines.append(line)
            else:
                filter_lines.append(line)

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
    parser.add_argument('--toggle', '-t', required=False, help='The toggle file you want to use')
    parser.add_argument('--spirit', '-s', required=True, help='The path to the filter spirit executable')
    parser.add_argument('--output', '-o', default='xai.filter', help='The path you want to output the final filter to')
    parser.add_argument('--temp-file', default='_filter.tmp', help='Path to temporary file to store combined filter in')

    main(parser.parse_args())
