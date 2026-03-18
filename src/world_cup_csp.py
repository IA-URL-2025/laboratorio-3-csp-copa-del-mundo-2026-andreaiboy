import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        teams_in_group = [t for t, g in assignment.items() if g == group]

        # 1. Restricción de tamaño máximo 4
        if len(teams_in_group) >= 4:
            return False
        
        # 2. Restricción de bombos: no puede haber dos del mismo bombo
        team_pot = self.get_team_pot(team)
        for assigned_team in teams_in_group:
            if self.get_team_pot(assigned_team) == team_pot:
                return False
            
         # 3. Restricción de confederaciones
        team_conf = self.get_team_confederation(team)

        conf_count = {}
        for assigned_team in teams_in_group:
            conf = self.get_team_confederation(assigned_team)
            conf_count[conf] = conf_count.get(conf, 0) + 1

        if team_conf == "UEFA":
            if conf_count.get("UEFA", 0) >= 2:
                return False
        else:
            if conf_count.get(team_conf, 0) >= 1:
                return False

        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)
        
        for var in self.variables:
            if var not in assignment:
                valid_groups = []

                for group in new_domains[var]:
                    if self.is_valid_assignment(group, var, assignment):
                        valid_groups.append(group)

                new_domains[var] = valid_groups

                if len(new_domains[var]) == 0:
                    return False, new_domains
        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        unassigned_vars = [v for v in self.variables if v not in assignment]

        if not unassigned_vars:
            return None

        return min(unassigned_vars, key=lambda var: len(domains[var]))

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: Si todas las variables están asignadas, retornamos la asignación.
        if len(assignment) == len(self.variables):
            return assignment

        # 1. Seleccionar variable con MRV
        var = self.select_unassigned_variable(assignment, domains)

        if var is None:
            return assignment
         # 2. Iterar sobre valores del dominio
        for group in domains[var]:
            # 3. Verificar si es válido
            if self.is_valid_assignment(group, var, assignment):
                if self.debug:
                    print(f"Intentando asignar {var} -> {group}")
                # Hacer asignación
                new_assignment = copy.deepcopy(assignment)
                new_assignment[var] = group

                # Reducir dominio de la variable ya asignada
                new_domains = copy.deepcopy(domains)
                new_domains[var] = [group]

                # Aplicar forward checking
                consistent, filtered_domains = self.forward_check(new_assignment, new_domains)

                if consistent:
                    result = self.backtrack(new_assignment, filtered_domains)
                    if result is not None:
                        return result

                if self.debug:
                    print(f"Backtrack en {var} -> {group}")

        # 5. Si nada funcionó, retornar fallo
        return None
