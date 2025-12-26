import subprocess


def set_route(number: int, dirprefix: str, netname: str, mode: str) -> None:
    # set current route for the SUMO simulation
    print(f'Setting route to {number}...')
    dir_name = f'{dirprefix}routes/{netname}/'
    file_names = ['bicycle.rou.xml', 'car.rou.xml', 'pedestrian.rou.xml']
    for f in file_names:
        subprocess.run(
            [
                'cp', f'{mode}/{number}/{f}', '.'
            ],
            check=True,
            cwd=dir_name
        )