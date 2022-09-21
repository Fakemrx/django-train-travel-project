from trains.models import Train


def get_routes(request, form) -> dict:
    qs = Train.objects.all()
    graph = get_graph(qs)
    data = form.cleaned_data
    from_city = data['from_city']
    to_city = data['to_city']
    travelling_time = data['travelling_time']
    cities = data['cities']
    all_ways = list(get_dfs_path(graph, from_city.pk, to_city.pk))
    context = {
        'form': form
    }
    if not len(all_ways):
        raise ValueError('Нет маршрута с заданными условиями')
    if cities:
        _cities = [city.id for city in cities]
        right_ways = []
        for route in all_ways:
            if all(city in route for city in _cities):
                right_ways.append(route)
            if not right_ways:
                raise ValueError('Маршрут через указанные города невозможен')
    else:
        right_ways = all_ways
    if travelling_time:
        trains = []
        all_trains = {}
        for q in qs:
            all_trains.setdefault((q.from_city_id, q.to_city_id), [])
            all_trains[(q.from_city_id, q.to_city_id)].append(q)
        for route in right_ways:
            tmp = dict()
            tmp['trains'] = []
            total_time = 0
            for i in range(len(route) - 1):
                qs = all_trains[(route[i], route[i + 1])]
                q = qs[0]
                total_time += q.travel_time
                tmp['trains'].append(qs)
            tmp['total_time'] = total_time
            if total_time <= travelling_time:
                trains.append(tmp)
        if not trains:
            raise ValueError('Нет маршрутов с временем меньше указанного')
    return context


def get_graph(qs):
    graph = {}
    for q in qs:
        graph.setdefault(q.from_city_id, set())
        graph[q.from_city_id].add(q.to_city_id)
    return graph


def get_dfs_path(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        if vertex in graph.keys():
            for next_ in graph[vertex] - set(path):
                if next_ == goal:
                    yield path + [next_]
                else:
                    stack.append((next_, path + [next_]))
