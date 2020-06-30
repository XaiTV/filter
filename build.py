import argparse
import glob
import os


def get_var_from_line(line):
    split_line = line.strip().split(' ')
    if split_line[0].startswith('$'):
        return split_line[0]
    else:
        return None


def generate_filter_version(spirit, var_base_file, filter_file, output_path, var_file=None, toggle_file=None, temp_file='_filter.tmp'):
    with open(var_base_file, 'r') as fp:
        var_lines = fp.readlines()
    
    if var_file:
        new_lines = []
        with open(var_file, 'r') as fp:
            for line in fp.readlines() + var_lines:
                var = get_var_from_line(line)
                # if the var isn't used before, the line can be added
                if var is None or not any(get_var_from_line(line2) == var for line2 in new_lines):
                    new_lines.append(line)

        var_lines = new_lines

    toggles = {}
    if toggle_file:
        with open(toggle_file, 'r') as fp:
            for line in fp.readlines():
                line = line.strip()
                if line.startswith('$'):
                    toggle_name, toggle_value = line.split('=')
                    toggle_name = toggle_name.strip()[1:]
                    toggle_value = toggle_value.strip()
                    toggles[toggle_name] = toggle_value

    with open(filter_file, 'r') as fp:
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
                    
                    line = '#TOGGLE-'.join([pre_toggle, after_toggle])
                
                filter_lines.append(line)
            else:
                filter_lines.append(line)

    # let's be nice and add a newline between the var and filter
    combined_lines = var_lines + ['\n'] + filter_lines

    with open(temp_file, 'w') as fp:
        fp.writelines(combined_lines)

    # @TODO: don't use os.system, it's lame and potentially unsafe
    os.system('{0} -g --input-path {1} --output-path={2} -e'.format(
        spirit, temp_file, output_path,
    ))
    print('Filter now available at: {0}'.format(output_path))


def main(args):
    var_files = [None]
    if args.var_directory:
        var_files += glob.glob(os.path.join(args.var_directory, '*.vars'))

    toggle_files = [None]
    if args.toggle_directory:
        toggle_files += glob.glob(os.path.join(args.toggle_directory, '*.toggle'))

    output_path = '/'.join(args.output.split('/')[:-1])
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for var_file in var_files:
        for toggle_file in toggle_files:
            output_name = '{0}'.format(args.output)
            if toggle_file:
                output_name += '.{0}'.format(toggle_file.split('/')[-1][:-7])
            else:
                output_name += '.generic'

            if var_file:
                output_name += '.{0}'.format(var_file.split('/')[-1][:-5])

            output_name += '.filter'

            generate_filter_version(
                args.spirit,
                args.var_base_file,
                args.filter,
                output_name,
                var_file,
                toggle_file,
                args.temp_file,
            )

    print('All filters generated')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter Spirit variable helper')
    parser.add_argument('--var-base-file', '-b', default='base.vars', help='The variable file you want to use as a base')
    parser.add_argument('--var-directory', '-v', required=False, help='The directory with .vars files in it to base filter variations on')
    parser.add_argument('--filter', '-f', default='xai.filter_spirit', help='The filter file you want to use')
    parser.add_argument('--toggle-directory', '-t', required=False, help='The directory with toggle files in it')
    parser.add_argument('--spirit', '-s', required=True, help='The path to the filter spirit executable')
    parser.add_argument('--output', '-o', default='output/xai', help='The filter output path BEFORE the .filter. So for example: output/xai will become output/xai.generic.filter and output/xai.strict.filter.')
    parser.add_argument('--temp-file', default='_filter.tmp', help='Path to temporary file to store combined filter in')

    main(parser.parse_args())
