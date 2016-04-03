import anuga

cache = False
verbose = True

with_gate = False  # second case with artificial water gate?

if with_gate:
    name = 'jakarta_flood2_x'
    dem_asc_file = 'data/dem_x.asc'
    dem_cdf_file = 'data/dem_x.dem'
    dem_pts_file = 'data/dem_x.pts'
    mesh_file = 'jakarta_x.msh'
else:
    name = 'jakarta_flood2'
    dem_asc_file = 'data/dem.asc'
    dem_cdf_file = 'data/dem.dem'
    dem_pts_file = 'data/dem.pts'
    mesh_file = 'jakarta.msh'

init_stage = 17
inflow_stage = init_stage+10+5

base_scale = 2  # 1 -> ~3 meter wide triangles
default_res = 100 * base_scale   # Background resolution

# coordinates extracted out of boundary layer
bounding_polygon = [(704627,9.30357e+06), (704937,9.30354e+06), (705274,9.30368e+06), (705246,9.30445e+06), (704679,9.30491e+06), (704646,9.30526e+06), (705521,9.30634e+06), (705961,9.30702e+06), (706430,9.30703e+06), (706449,9.30741e+06), (706229,9.30769e+06), (704918,9.30769e+06), (704890,9.30667e+06), (704019,9.30582e+06), (704057,9.30488e+06), (703789,9.30459e+06), (704359,9.3042e+06), (704627,9.30357e+06)]

# Create NetCDF file from asc data
res = anuga.asc2dem(dem_asc_file, use_cache=cache, verbose=verbose)

# Create pts file from dem
anuga.dem2pts(dem_cdf_file, use_cache=cache, verbose=verbose)

interior_regions = [] # this makes huge mesh [bounding_polygon, base_scale] ]

# name + list of segments
boundary_tags = { 'in': [0] } # {'in': [0], 'other': [1,2,3,4] }

#------------------------------------------------------------------------------
# Create the triangular mesh and domain based on
# overall clipping polygon with a tagged
# boundary and interior regions as defined in project.py
#------------------------------------------------------------------------------
domain = anuga.create_domain_from_regions(bounding_polygon,
                                    boundary_tags=boundary_tags,
                                    maximum_triangle_area=default_res,
                                    mesh_filename=mesh_file,
                                    interior_regions=interior_regions,
                                    use_cache=cache,
                                    verbose=verbose)


# Print some stats about mesh and domain
print 'Number of triangles = ', len(domain)
print 'The extent is ', domain.get_extent()
print domain.statistics()

domain.set_name(name) # Name of sww file
domain.set_datadir('.')                       # Store sww output here
#domain.set_minimum_storable_height(0.01)      # Store only depth > 1cm
domain.set_flow_algorithm('DE0')

domain.set_quantity('stage', init_stage)
domain.set_quantity('friction', 1.0)

domain.set_quantity('elevation',
                    filename=dem_pts_file,
                    use_cache=cache,
                    verbose=verbose,
                    alpha=0.1)


Bd = anuga.Dirichlet_boundary([inflow_stage, 0, 0]) # Mean water level
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Neutral boundary

domain.set_boundary({'in': Bd,
                      'exterior': Bs, })

for t in domain.evolve(yieldstep=60, finaltime=3600*5):
    print domain.timestepping_statistics()
