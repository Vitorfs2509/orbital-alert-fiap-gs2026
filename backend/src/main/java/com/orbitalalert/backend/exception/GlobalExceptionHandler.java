package com.orbitalalert.backend.exception;
import org.springframework.http.*;import org.springframework.web.bind.MethodArgumentNotValidException;import org.springframework.web.bind.annotation.*;import java.time.LocalDateTime;import java.util.Map;
@RestControllerAdvice
public class GlobalExceptionHandler {
 @ExceptionHandler(NotFoundException.class) ResponseEntity<?> nf(NotFoundException e){return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("timestamp",LocalDateTime.now(),"error",e.getMessage()));}
 @ExceptionHandler(BadRequestException.class) ResponseEntity<?> br(BadRequestException e){return ResponseEntity.badRequest().body(Map.of("timestamp",LocalDateTime.now(),"error",e.getMessage()));}
 @ExceptionHandler(MethodArgumentNotValidException.class) ResponseEntity<?> mv(MethodArgumentNotValidException e){return ResponseEntity.badRequest().body(Map.of("timestamp",LocalDateTime.now(),"error","Dados inválidos","details",e.getBindingResult().getFieldErrors().stream().map(f->f.getField()+": "+f.getDefaultMessage()).toList()));}
}
