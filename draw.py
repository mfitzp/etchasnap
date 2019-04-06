import sys


from PIL import Image
import graph, plotter, camera



def main():
    image = Image.open(sys.argv[1])
    image = camera.process_image(image)
    moves = graph.generate_moves(image)
    plotter.enqueue(moves)

    
if __name__ == "__main__":
    main()