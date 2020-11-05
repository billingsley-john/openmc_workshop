

import openmc

mats = openmc.Materials()

cell_material = openmc.Material(1, "PbLi")  # Pb84.2Li15.8
cell_material.add_element('Pb', 84.2, percent_type='ao')
cell_material.add_element('Li', 15.8, percent_type='ao', enrichment=7.0, enrichment_target='Li6', enrichment_type='ao')   # natural enrichment = 7% Li6. Change enrichment here.
cell_material.set_density('g/cm3', 11.0)
mats.append(cell_material)


# GEOMETRY
sph1 = openmc.Sphere(r=50)
sph2 = openmc.Sphere(r=80, boundary_type='vacuum')
sph3 = +sph1 & -sph2

geometry_cell = openmc.Cell(region=sph3)
geometry_cell.fill = cell_material

inner_vacuum_cell = openmc.Cell(region=-sph1)

universe = openmc.Universe(cells=[inner_vacuum_cell, geometry_cell])

geom = openmc.Geometry(universe)


# SIMULATION SETTINGS

# Instantiate a Settings object
sett = openmc.Settings()
batches = 2
sett.batches = batches
sett.inactive = 0
sett.particles = 50000
sett.particle = "neutron"
sett.run_mode = 'fixed source'

# creates a 14MeV point source
source = openmc.Source()
source.space = openmc.stats.Point((0, 0, 0))
source.angle = openmc.stats.Isotropic()
source.energy = openmc.stats.Discrete([14e6], [1])
sett.source = source

# filters
cell_filter = openmc.CellFilter(geometry_cell)
energy_bins_n, dose_coeffs_n = openmc.data.dose_coefficients(particle='neutron', geometry='AP')
energy_function_filter_n = openmc.EnergyFunctionFilter(energy_bins_n, dose_coeffs_n)

my_tally = openmc.Tally(name='tally')
my_tally.scores = ['current']
my_tally.filters = [cell_filter, energy_function_filter_n]

tallies = openmc.Tallies()
tallies.append(my_tally)

model = openmc.model.Model(geom, mats, sett, tallies)
results_filename = model.run()

# open the results file
results = openmc.StatePoint(results_filename)

#extracts the tally values from the simulation results
tally_results = results.get_tally(name='tally')
df = tally_results.get_pandas_dataframe()

result = df['mean'].sum()
print(result)
