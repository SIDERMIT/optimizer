import filecmp
import os
import unittest
from pathlib import Path


from sidermit import exceptions
from sidermit import graph
from sidermit import transport_mode
from sidermit import transport_network




class test_graph(unittest.TestCase):

    def setUp(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.data_path = os.path.join(self.dir_path, 'file')
        self.data_path = os.path.join(self.data_path, 'transport_network')

    def test_routes(self):
        """
        test Route class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()

        r = transport_network.Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(isinstance(r, transport_network.Route))

    def test_raises_routes_exceptions(self):
        """
        to check route class exceptions
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()

        with self.assertRaises(exceptions.RouteIdIsNotValidExceptions):
            transport_network.Route(g, m, None, "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        with self.assertRaises(exceptions.ModeNameIsNotValidExceptions):
            transport_network.Route(g, m, "r1", "train", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        with self.assertRaises(exceptions.SequencesLenExceptions):
            transport_network.Route(g, m, "r1", "bus", "1", "3,4,0,2,1", "1,0,3", "3,0,1")

        with self.assertRaises(exceptions.StopsSequencesExceptions):
            transport_network.Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,5,3", "3,0,1")

        with self.assertRaises(exceptions.FirstStopIsNotValidExceptions):
            transport_network.Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "2,0,3", "3,0,1")

        with self.assertRaises(exceptions.LastStopIsNotValidExceptions):
            transport_network.Route(g, m, "r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,2", "3,0,1")

        with self.assertRaises(exceptions.NotCycleExceptions):
            transport_network.Route(g, m, "r1", "bus", "1,2,0,4,3", "4,0,2,1", "1,0,3", "4,0,1")

        with self.assertRaises(exceptions.NodeSequencesIsNotValidExceptions):
            transport_network.Route(g, m, "r1", "bus", "1,3,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

    def test_add_route_transport_network(self):
        """
        to test add_route method of transport_network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(isinstance(t.get_route("r1"), transport_network.Route))
        self.assertEqual(len(t.get_routes()), 1)

        with self.assertRaises(exceptions.RouteIdDuplicatedExceptions):
            t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

    def test_delete_route_transport_network(self):
        """
        to test delete_route method of class transport_network class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        t.delete_route("r1")
        self.assertEqual(len(t.get_routes()), 0)

        with self.assertRaises(exceptions.RouteIdNotFoundExceptions):
            t.delete_route("r1")

    def test_network_to_file(self):
        """
        to test method to write a file with network information
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        t.add_route("r2", "metro", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")
        # write file
        t.routes_to_file(os.path.join(self.data_path, 'write_test.csv'))
        fileObj = Path(os.path.join(self.data_path, 'write_test.csv'))
        # test
        self.assertTrue(fileObj.is_file())
        # to compare file with a test file
        self.assertTrue(
            filecmp.cmp(os.path.join(self.data_path, 'write1_test.csv'),
                        os.path.join(self.data_path, "write_test.csv")))
        # remove file
        os.remove(os.path.join(self.data_path, 'write_test.csv'))

    def test_is_valid(self):
        """
        to test is_Valid method from transport network class
        :return:
        """

        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)
        t.add_route("r1", "bus", "1,2,0,4,3", "3,4,0,2,1", "1,0,3", "3,0,1")

        self.assertTrue(t.is_valid())

        t.delete_route("r1")

        self.assertTrue(not t.is_valid())

    def test_raises_get_route_exceptions(self):
        """
        raises get_route exceptions from transport network class
        :return:
        """
        with self.assertRaises(exceptions.RouteIdNotFoundExceptions):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = transport_mode.TransportMode()
            t = transport_network.TransportNetwork(g, m)
            t.get_route("r1")

    def test_build_from_file(self):
        """
        to test method build_from_file transport network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork.build_from_file(g, m, os.path.join(self.data_path, 'write1_test.csv'))

        self.assertEqual(len(t.get_routes()), 2)

    def test_raises_build_from_file_exceptions(self):
        """
        raises build_from_file exceptions from transport network class
        :return:
        """
        with self.assertRaises(exceptions.FileFormatIsNotValidException):
            g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
            m = transport_mode.TransportMode()
            transport_network.TransportNetwork.build_from_file(g, m, os.path.join(self.data_path,
                                                                                  'test_fileformatExceptions.csv'))

    def test_update_route(self):
        """
        to test update_route method from transport_network class
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork.build_from_file(g, m, os.path.join(self.data_path, 'write1_test.csv'))

        t.update_route("r1", mode_name="metro")
        self.assertEqual(t.get_route("r1").mode, "metro")

        t.update_route("r1")
        self.assertEqual(t.get_route("r1").mode, "metro")

        with self.assertRaises(exceptions.RouteIdNotFoundExceptions):
            t.update_route("r3")

    def test_add_radial_routes(self):
        """
        to test add radial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)

        t.add_radial_routes(0)

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("R_1").nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("R_1").nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("R_1").stops_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("R_1").stops_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("R_2").nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("R_2").nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(t.get_route("R_2").stops_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("R_2").stops_sequence_r, ["0", "4", "3"])

    def test_add_express_radial_routes(self):
        """
        to test add radial routes
        :return:
        """
        g = graph.Graph.build_from_parameters(5, 1000, 0.5, 2)
        m = transport_mode.TransportMode()
        t = transport_network.TransportNetwork(g, m)

        t.add_express_radial_routes()

        self.assertEqual(len(t.get_routes()), 5)
        self.assertEqual(t.get_route("ER_1").nodes_sequence_i, ["1", "2", "0"])
        self.assertEqual(t.get_route("ER_1").nodes_sequence_r, ["0", "2", "1"])
        self.assertEqual(t.get_route("ER_1").stops_sequence_i, ["1", "0"])
        self.assertEqual(t.get_route("ER_1").stops_sequence_r, ["0", "1"])
        self.assertEqual(t.get_route("ER_2").nodes_sequence_i, ["3", "4", "0"])
        self.assertEqual(t.get_route("ER_2").nodes_sequence_r, ["0", "4", "3"])
        self.assertEqual(t.get_route("ER_2").stops_sequence_i, ["3", "0"])
        self.assertEqual(t.get_route("ER_2").stops_sequence_r, ["0", "3"])
    
    def test_plot(self):
        """
        to test plot method
        :return: 
        """
        g = graph.Graph.build_from_parameters(7, 1000, 0.5, 0, angles=[10, 50, 150, 180, 270, 300, 320], etha=0.5,
                                              etha_zone=3,
                                              Hi=[1, 2, 1, 1, 1, 0.5, 3], Gi=[1, 2, 1, 1, 1, 3, 2])

        m = transport_mode.TransportMode(add_default_mode=True)

        t = transport_network.TransportNetwork(g, m)
        t.add_express_radial_routes(index_mode=0)
        # save figure in path
        t.plot(os.path.join(self.data_path, 'figure1_test.png'))
        fileObj = Path(os.path.join(self.data_path, 'figure1_test.png'))
        # test
        self.assertTrue(fileObj.is_file())
        # to compare figure with a test figure
        self.assertTrue(
            filecmp.cmp(os.path.join(self.data_path, 'figure_test.png'),
                        os.path.join(self.data_path, "figure1_test.png")))

        # remove file
        os.remove(os.path.join(self.data_path, 'figure1_test.png'))

        with self.assertRaises(exceptions.RouteIdNotFoundExceptions):
            t.plot(os.path.join(self.data_path, 'figure_test.png'), list_routes=["506"])


if __name__ == '__main__':
    unittest.main()
