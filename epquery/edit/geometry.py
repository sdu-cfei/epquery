from epquery import BasicEdit
from epquery import utilities


class Geometry(BasicEdit):
    """
    Geometry specific methods.
    """

    def get_surface_area(self, surface_name, surface_type='BuildingSurface:Detailed'):
        """
        Returns the surface area.

        :param str surface_name: Surface name
        :param str surface_type: Surface type, default: BuildingSurface:Detailed
        :returns: List of vertices (list of tuples with x, y, z)
        :rtype: list(tuple(float, float, float))
        """
        vertices = self.get_surface_vertices(surface_name, surface_type)

        # TODO: convert 3D polygon to 2D and use utilities.polygon_area()
        raise NotImplemented('Method not implemented yet')

    def get_surface_vertices(self, surface_name, surface_type='BuildingSurface:Detailed'):
        """
        Returns a list of vertices defining the surface.

        :param str surface_name: Surface name
        :param str surface_type: Surface type, default: BuildingSurface:Detailed
        :returns: List of vertices (list of tuples with x, y, z)
        :rtype: list(tuple(float, float, float))
        """
        def vertex_field(num, xyz):
            return 'Vertex {} {}-coordinate'.format(num, xyz.upper())

        vertices = list()

        surface = self.filter(
            self.mask(surface_type, Name=surface_name)
            )[0]

        # Find all vertices
        count = 1
        while True:

            try:
                x = float(self.get_field(surface, vertex_field(count, 'X')))
                y = float(self.get_field(surface, vertex_field(count, 'Y')))
                z = float(self.get_field(surface, vertex_field(count, 'Z')))

                vertices.append((x, y, z))
            except IndexError:
                # End of vertices
                break

            count += 1

        return vertices

    def get_surface_centroid(self, surface_name, surface_type='BuildingSurface:Detailed',
                             relative=False):
        """
        Returns the surface center point (centroid). The centroid can be in absolute
        or relative coordinates (relative to the first vertex).

        :param str surface_name: Surface name
        :param str surface_type: Surface type, default: BuildingSurface:Detailed
        :param bool relative: If *True* the centroid is given in relative coordinates
        :rtype: numpy.ndarray with 3 elements
        """
        logger.debug('Calculating surface centroid for: {}'.format(surface_name))

        vertices = np.array(self.get_surface_vertices(surface_name, surface_type))
        logger.debug('Vertices:\n{}'.format(vertices))

        if relative:
            # move polygon so that it starts at x=0, y=0, z=0
            vertices = vertices - np.min(vertices, 0)
            logger.debug('Vertices after transformation to origin:\n{}'.format(vertices))

        c = np.sum(vertices, 0) / len(vertices)
        logger.debug('Centroid: {}'.format(c))

        return c