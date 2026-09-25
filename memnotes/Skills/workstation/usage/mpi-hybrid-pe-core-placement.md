---
type: Domain Topic
id: workstation/usage/mpi-hybrid-pe-core-placement
domain: workstation
audience: usage
artifact_role: guideline
status: draft
summary: Place and audit MPI rank pinning on the hybrid P/E-core i9-13900KF workstation with Open MPI 5.0.8; PRTE placement flags fail, use a rankfile.
triggers: [MPI pinning, P-cores, E-cores, rankfile, PRTE, mpirun placement]
source_project: native
source_sha256: empty
aliases: [MPI core placement]
---

# MPI placement on the hybrid P/E-core workstation (Open MPI 5.0.8 / PRTE)

Use this topic when MPI jobs on the i9-13900KF workstation use only 8 cores, when concurrent MPI jobs must split across P-cores and E-cores, or when auditing rank placement.

## Topology

- CPUs 0-15 are 8 P-cores with 2 hyperthreads each at 5.5-5.8 GHz. CPUs 16-31 are 16 E-cores without hyperthreads at 4.3 GHz. P-cores come first in enumeration.
- `mpirun` maps one rank per core in enumeration order and binds each rank to its whole core. `-np 8` uses exactly the 8 P-cores; E-cores stay idle. `-np 16` uses 8 P-cores plus 8 E-cores. `-np 24` uses all cores. This mapping is not a fault.

## Audit placement of a live job

```bash
pgrep -af 'mpirun|prte|abinit|siesta'
awk '/Cpus_allowed_list/{print $2}' /proc/<pid>/status   # binding mask
awk '{print $39}' /proc/<pid>/stat                        # current CPU
```

`ps -o psr` is unsupported on this box. Concurrent default-mapped jobs all bind inside CPUs 0-15 and time-share the P-cores while E-cores idle.

## Pin a job to E-cores

PRTE placement flags all fail on this hybrid topology. `--cpu-list`, `--map-by pe-list=`, and `taskset -c 16-31 mpirun` give slot errors, garbage bindings, or silent override. Use a rankfile with logical core indices; logical 8-23 are the E-cores (physical CPUs 16-31):

```
echo 'rank 0=+n0 slot=8' > rf    # one line per rank: slot=8+i
mpirun --map-by rankfile:file=rf -np N ./app
```

Verified: `slot=8-11` places ranks on CPUs 16-19.

## Performance caveats

- One E-core rank is about 30 percent slower than one P-core rank. MPI paces to the slowest rank, so `-np 8` P-only is often within noise of `-np 16`. Measure before choosing.
- Avoid `--use-hwthread-cpus`: it puts 2 ranks on each P-core.
- The omp harness exports `OMP_NUM_THREADS=1` into `mpirun` sessions. Set the variable explicitly for hybrid MPI plus OpenMP runs.
