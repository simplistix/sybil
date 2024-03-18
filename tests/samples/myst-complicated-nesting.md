# {py:mod}`bytewax.connectors.demo`

```{py:module} bytewax.connectors.demo
```

```{autodoc2-docstring} bytewax.connectors.demo
:parser: myst
:allowtitles:
```

## Data

````{py:data} X
:canonical: bytewax.connectors.demo.X
:type: typing.TypeVar

```{autodoc2-docstring} bytewax.connectors.demo.X
:parser: myst
```

````


## Classes

`````{py:class} RandomMetricSource(metric_name: str, interval: datetime.timedelta = timedelta(seconds=0.7), count: int = sys.maxsize, next_random: typing.Callable[[], float] = lambda: random.randrange(0, 10))
:canonical: bytewax.connectors.demo.RandomMetricSource

:Bases:
    - {py:obj}`~bytewax.inputs.FixedPartitionedSource``[`{py:obj}`~typing.Tuple``[`{py:obj}`~str``, `{py:obj}`~float``], `{py:obj}`~bytewax.connectors.demo._RandomMetricState``]`

```{autodoc2-docstring} bytewax.connectors.demo.RandomMetricSource
:parser: myst
```

```{rubric} Initialization
```

```{autodoc2-docstring} bytewax.connectors.demo.RandomMetricSource.__init__
:parser: myst
```

````{py:method} list_parts() -> typing.List[str]
:canonical: bytewax.connectors.demo.RandomMetricSource.list_parts

````

````{py:method} build_part(now: datetime.datetime, for_part: str, resume_state: typing.Optional[bytewax.connectors.demo._RandomMetricState])
:canonical: bytewax.connectors.demo.RandomMetricSource.build_part

````

`````
